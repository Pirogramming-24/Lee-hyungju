import cv2
import mediapipe as mp

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

# 손가락 팁과 PIP 인덱스 (엄지 제외)
FINGER_TIPS = [8, 12, 16, 20]   # index, middle, ring, pinky
FINGER_PIPS = [6, 10, 14, 18]


def is_thumb_open(lms, handedness: str) -> bool:
    """
    엄지 펼침 판별.
    - x축 상대 위치를 사용(오른손/왼손 반전 고려).
    """
    tip = lms.landmark[4].x
    ip  = lms.landmark[3].x
    mcp = lms.landmark[2].x
    if handedness == "Right":
        return tip > ip > mcp
    else:
        return tip < ip < mcp


def is_finger_up(lms, tip_idx: int, pip_idx: int) -> bool:
    """
    단순 기준: 팁 y < PIP y 면 '펴짐'
    손목 회전/기울기에 민감하지만, 가볍고 빠름.
    """
    return lms.landmark[tip_idx].y < lms.landmark[pip_idx].y


def get_fingers_state(lms):
    """
    각 손가락 펴짐 여부 반환 (엄지 제외 4개).
    returns: dict with keys: index, middle, ring, pinky
    """
    good_up  = is_finger_up(lms, FINGER_TIPS[0], FINGER_PIPS[0])
    idx_up   = is_finger_up(lms, 8, 6)
    mid_up   = is_finger_up(lms, 12, 10)
    ring_up  = is_finger_up(lms, 16, 14)
    pinky_up = is_finger_up(lms, 20, 18)
    return {
        "thumb": good_up,
        "index": idx_up,
        "middle": mid_up,
        "ring": ring_up,
        "pinky": pinky_up,
    }


def count_open_fingers(lms, handedness: str) -> int:
    """
    펴진 손가락 개수 카운트(엄지 포함).
    """
    states = get_fingers_state(lms)
    open_cnt = sum(states.values())
    if is_thumb_open(lms, handedness):
        open_cnt += 1
    return open_cnt


def classify_rps(lms, handedness: str) -> str:
    """
    패턴 우선 규칙:
      1) 가위: 검지·중지 펴짐 AND 약지·소지 접힘 (엄지는 무시)
      2) 보  : 5개(엄지 포함) 모두 펴짐(또는 4개 이상으로 완전 펴짐에 가깝게)
      3) 바위: 0~1개만 펴짐
      4) 나머지(3~4개 등): 보로 처리(오판시 보정 용이)
    """
    s = get_fingers_state(lms)

    # 1) '가위'는 '검/중 up AND 약/소 down'로만 인정
    open_cnt = count_open_fingers(lms, handedness)
    if s["index"] and s["middle"] and (not s["ring"]) and (not s["pinky"]):
        return "scissors"

    if s["thumb"] and s["index"] and (not s["ring"]) and (not s["pinky"]) and (not s["middle"]):
        return "scissors"

    # 2) 보: 거의 다 펴진 경우
    if open_cnt >= 5 :
        return "paper"

    # 3) 바위: 거의 다 접힌 경우
    if open_cnt < 1:
        return "rock"

    # 4) 그 외: none
    return "none"


def main():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("웹캠을 열 수 없습니다.")
        return

    with mp_hands.Hands(
        max_num_hands=1,
        model_complexity=0,
        min_detection_confidence=0.6,
        min_tracking_confidence=0.6
    ) as hands:

        last_label, stable_label, same_count = "", "", 0  # 디바운싱

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            # 미러 편의: 좌우반전 후 처리
            frame = cv2.flip(frame, 1)
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            result = hands.process(rgb)

            label_to_draw = ""

            if result.multi_hand_landmarks and result.multi_handedness:
                hand_landmarks = result.multi_hand_landmarks[0]
                handedness = result.multi_handedness[0].classification[0].label  # "Left"/"Right"

                # 분류
                label = classify_rps(hand_landmarks, handedness)

                # 디바운싱: 같은 결과가 연속 N프레임 나오면 확정
                if label == last_label:
                    same_count += 1
                else:
                    same_count = 0
                last_label = label

                if same_count > 3:  # 4프레임 연속 같으면 표시
                    stable_label = label
                label_to_draw = stable_label or label

                # 랜드마크 그리기(디버그)
                mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            # 라벨 표시
            if label_to_draw:
                cv2.rectangle(frame, (20, 20), (220, 90), (0, 0, 0), -1)
                cv2.putText(frame, f"{label_to_draw}", (30, 75),
                            cv2.FONT_HERSHEY_SIMPLEX, 1.8, (255, 255, 255), 3, cv2.LINE_AA)

            cv2.imshow("RPS Detection (q: 종료)", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
