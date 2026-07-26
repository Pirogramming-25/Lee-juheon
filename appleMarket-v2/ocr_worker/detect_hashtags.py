import sys
import json
from ultralytics import YOLO

# YOLO11n(nano, 가장 가벼운 버전) 사전 학습 모델 사용
model = YOLO('yolo11n.pt')


def main():
    image_path = sys.argv[1]

    results = model(image_path)

    labels = set()
    for result in results:
        for box in result.boxes:
            cls_id = int(box.cls[0])
            label = model.names[cls_id]
            labels.add(label)

    hashtags = ['#' + label.replace(' ', '_') for label in labels]

    print(json.dumps({'hashtags': hashtags}, ensure_ascii=False))


if __name__ == '__main__':
    main()