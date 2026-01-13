import mediapipe as mp
import math, time
import cv2 as cv
from mediapipe.tasks.python import vision
from mediapipe.tasks import python
from mediapipe.tasks.python.vision.core.vision_task_running_mode import VisionTaskRunningMode


from visualization import draw_manual, print_RSP_result
## 필요한 함수 작성


def _finger_extended(lm, tip, pip):
    # 이미지 좌표계: y가 위->아래로 증가, tip이 더 위면 펼쳐짐
    return lm[tip].y < lm[pip].y

def _thumb_extended(lm, handedness_label: str):
    # 엄지는 x축 기준
    # Right: tip.x > ip.x
    # Left : tip.x < ip.x
    if handedness_label.lower() == "right":
        return lm[4].x > lm[3].x
    else:
        return lm[4].x < lm[3].x
    
def classify_rps(detection_result):
    if detection_result is None or not detection_result.hand_landmarks:
        return None
    lm = detection_result.hand_landmarks[0]

    handedness_label = "Right"
    try:
        handedness_label = detection_result.handedness[0][0].category_name
    except Exception:
        pass

    
    thumb = _thumb_extended(lm, handedness_label)
    idx = _finger_extended(lm, 8, 6)
    mid = _finger_extended(lm, 12, 10)
    ring = _finger_extended(lm, 16, 14)
    pinky = _finger_extended(lm, 20, 18)

    # 가위
    if ((idx and mid and (not ring) and (not pinky)) or
        (thumb and idx and (not mid) and (not ring) and (not pinky))):
        return 2
    
    # 바위
    if (not idx) and (not mid) and (not ring) and (not pinky):
        return 0
    
    # 보
    if idx and mid and ring and pinky and thumb:
        return 1
    
    return -1

def main():
    base_options = python.BaseOptions(model_asset_path="hand_landmarker.task")
    options = vision.HandLandmarkerOptions(
        base_options = base_options,
        running_mode = VisionTaskRunningMode.VIDEO,
        num_hands=1
    )
    landmarker = vision.HandLandmarker.create_from_options(options)

    cap = cv.VideoCapture(0)
    if not cap.isOpened():
        print("Cannot open camera")
        exit()
    start= time.time()

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Can't receive frame. Exiting ...")
            break

        rgb = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)

        ts = int((time.time() - start) * 1000)
        detection_result = landmarker.detect_for_video(mp_image, ts)

        rps_result = classify_rps(detection_result)

        frame = draw_manual(frame, detection_result)
        frame = print_RSP_result(frame, rps_result)
    
        cv.imshow("RPS", frame)
        if cv.waitKey(1) == ord("q"):
            break

    cap.release()
    cv.destroyAllWindows()

if __name__ == "__main__":
    # 실행 로직
    main()