 #!/bin/bash
 python WebGen.py \
	--testing ./containers_only_val_image \
	--testing-p2p \
		--testing-p2p-weights ./model/pix2pix/out/transfer_learning/ \
		--testing-p2p-yolo-weights ./model/keras-yolo3/model_data/containers_transferlearning.h5 \
	--testing-classes ./model/classes.txt \
	-o ./generated/pix2pix/transferlearning/
