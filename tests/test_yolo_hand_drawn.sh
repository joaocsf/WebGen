 #!/bin/bash
 python WebGen.py \
	--testing ./dataset_no_containers_validation \
	--testing-yolo \
		--testing-yolo-weights ./model/keras-yolo3/model_data/elements_hand_original_weights.h5 \
	--testing-classes ./model/classes.txt \
	-o ./generated/yolo/hand_drawn/
