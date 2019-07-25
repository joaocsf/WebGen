 #!/bin/bash
 python WebGen.py \
	--testing ./containers_only_val_image \
	--testing-p2p \
		--testing-p2p-weights ./model/pix2pix/out/only_drawings/ \
		--testing-p2p-yolo-weights ./model/keras-yolo3/model_data/containers_hand_original_weights.h5 \
	--testing-classes ./model/classes.txt \
	-o ./generated/pix2pix/hand_drawn/
