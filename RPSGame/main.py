import cv2 as cv
import mediapipe as mp
import math, time
from mediapipe.tasks.python import vision

from visualization import draw_manual, print_RSP_result

MODEL_PATH = "hand_landmarker.task"

# LIVE_STREAM 모드는 비동기 콜백으로 결과가 오기 때문에,
# 가장 최근 결과를 담아둘 전역 변수가 필요함
latest_result = None


def result_callback(result, output_image, timestamp_ms):
    global latest_result
    latest_result = result


def create_landmarker():
    base_options = mp.tasks.BaseOptions(model_asset_path=MODEL_PATH)
    options = vision.HandLandmarkerOptions(
        base_options=base_options,
        running_mode=vision.RunningMode.LIVE_STREAM,
        num_hands=1,
        result_callback=result_callback,
    )
    return vision.HandLandmarker.create_from_options(options)


def distance(p1, p2):
    return math.hypot(p1.x - p2.x, p1.y - p2.y)


def classify_rps(hand_landmarks):
    """
    엄지를 제외한 검지~소지 4개 손가락에 대해
    TIP-WRIST 거리와 PIP-WRIST 거리를 비교해 펴짐/접힘을 판단하고,
    펴진 손가락 개수로 가위/바위/보를 구분한다.
    0 == rock, 1 == paper, 2 == scissors
    """
    wrist = hand_landmarks[0]

    # (TIP index, PIP index)
    finger_joints = [
        (8, 6),    # 검지
        (12, 10),  # 중지
        (16, 14),  # 약지
        (20, 18),  # 소지
    ]

    extended_count = 0
    for tip_idx, pip_idx in finger_joints:
        tip_dist = distance(hand_landmarks[tip_idx], wrist)
        pip_dist = distance(hand_landmarks[pip_idx], wrist)
        if tip_dist > pip_dist:
            extended_count += 1

    if extended_count == 0:
        return 0  # 바위 (rock)
    elif extended_count == 2:
        return 2  # 가위 (scissors)
    elif extended_count >= 4:
        return 1  # 보 (paper)
    else:
        return None  # 애매한 중간 상태는 판별하지 않음


if __name__ == "__main__":
    landmarker = create_landmarker()
    cap = cv.VideoCapture(0)

    if not cap.isOpened():
        print("Cannot open camera")
        exit()

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Can't receive frame (stream end?). Exiting ...")
            break

        frame = cv.flip(frame, 1)  # 거울모드로 보기 편하게
        rgb_frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
        timestamp_ms = int(time.time() * 1000)

        landmarker.detect_async(mp_image, timestamp_ms)

        rps_result = None
        if latest_result and latest_result.hand_landmarks:
            rps_result = classify_rps(latest_result.hand_landmarks[0])

        frame = draw_manual(frame, latest_result)
        frame = print_RSP_result(frame, rps_result)

        cv.imshow("RPS Game", frame)

        if cv.waitKey(1) == ord('q'):
            break

    cap.release()
    cv.destroyAllWindows()
    landmarker.close()