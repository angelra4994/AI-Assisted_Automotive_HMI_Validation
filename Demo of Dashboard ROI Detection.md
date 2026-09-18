>Below image is the demo workbench, where:
* Laptop simulating the cluster vehicle reproducing a video
* Microsoft HD-3000 webcam
	**Photo Resolution: 4 MP
    Video Resolution: 1280 x 720 pixels (HD – 16:9)
    Frame Rate: 30 frames per second (FPS)
* HP ZDisplay used to print the inferences
* Jetson Orin Nano Super deploying yolo25n model

![[Prototype.png]]
## Dataset 
> **Ultralytics ✅
 * open-weigh, so after labeling the model is available without additional cost
 * From video of 20min just 26 frames available
 * Labeling process aceptable
 * ~30min expended for 26 frames labeling
+ [Optimistic Crane Dataset by Angel R](https://platform.ultralytics.com/angel-r/datasets/optimistic-crane)
* Model trained with 6 classes
![[Pasted image 20260918104821.png]]

> **Roboflow 🚧
 * Model weights not available on a free account
 * Configurable the number of frames to take from video
 * Platform expect on database labeling 
* ~1.5h for 200 frames labeling
* [Find green arrow and pointer Model > Overview](https://universe.roboflow.com/angels-workspace-bppk3/find-green-arrow-and-pointer)

## Train
> **Jetson Orin Nano Super
 * Limited resources, so not recommended for training
> **Google colab
 * Without account, time-box of GPU uses

See [[Model weights]] to see the training results and the "**best" model

## Deployment
- See [[Headless live USB-camera object detection with a YOLO26n TensorRT engine on Jetpack 6]] to see the fallowed steps for training and deployment on Jetson Orin Nano Super
- 
![[My movie 1_1.mp4]]

## MLOps
> Weights and Biases
 * To be integrated

## IDE
#### Headless
* [Remote Development using SSH](https://code.visualstudio.com/docs/remote/ssh)
* VS code with GitHub copilot integrated
* Jetson as server, with gnome disabled
* Docker container compatible with Jetpack 6.2
![[Pasted image 20260918082152.png]]

#### GUI active
* Native Ultralytics YOLO26n working on virtual environment (venv) 
* Jetpack 7.2




