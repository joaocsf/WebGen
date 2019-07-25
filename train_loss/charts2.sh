python ../utils/chart_from_history.py yolo/container_hand_drawn_history.pkl -i 0 -t "YOLO Containers Hand-Drawings"
python ../utils/chart_from_history.py yolo/container_transfer_learning_loss.pkl -i 0 -t "YOLO Containers Fine-Tune"
python ../utils/chart_from_history.py yolo/original_weights_loss_history.pkl -i 0 -t "YOLO Elements Hand-Drawings"
python ../utils/chart_from_history.py yolo/transfer_learning_loss_history.pkl -i 0 -t "YOLO Elements Fine-Tune"
python ../utils/chart_from_history.py pix2pix/only_hand-drawn_history.pkl -i 0 -t "Pix2Pix Hand-Drawings"
python ../utils/chart_from_history.py pix2pix/transfer-learning_history.pkl -i 0 -t "Pix2Pix Fine-Tune"

