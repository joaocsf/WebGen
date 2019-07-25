 #!/bin/bash
 python WebGen.py \
	--testing ./everything_val \
	--testing-yolo \
		--testing-yolo-weights ./model/keras-yolo3/model_data/elements_hand_original_weights.h5 \
	--testing-p2p \
		--testing-p2p-weights ./model/pix2pix/out/only_drawings/ \
		--testing-p2p-yolo-weights ./model/keras-yolo3/model_data/containers_hand_original_weights.h5 \
	--testing-classes ./model/classes.txt \
	-o ./generated/global/hand_drawn/
