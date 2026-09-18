The target of this section is present the flow to start live inferences using headless IDE [[Demo of Dashboard ROI Detection#Headless]]

## Start with docker
According to [Ultralytics Doc](https://docs.ultralytics.com/guides/nvidia-jetson#quick-start-with-docker)

*t=ultralytics/ultralytics:latest-jetson-jetpack6
sudo docker run -it --ipc=host --runtime=nvidia $t

Then, on my environment I need to 

sudo docker run -it --ipc=host --runtime=nvidia -v /yolo:/home/yolo ultralytics/ultralytics:latest-jetson-jetpack6

## Training


"""
 ULTRALYTICS_API_KEY="ul_45c080d25139772a8d1be1708ea160c24fc0e8b0" yolo train   model="ul://ultralytics/yolo26/yolo26n"   data="ul://angel-r/datasets/optimistic-crane"   task="detect"   epochs=200   batch=-1   imgsz=640   project="angel-r/example-project"  
"""

Model=yolo26n
epochs=200
Imgsz=640


## Export from pt to engine

""
yolo export model=/ultralytics/runs/detect/angel-r/example-project/train-2/weights/best.pt format=engine
""


## Python Script

 python3 /home/yolo/live_detect.py --model /ultralytics/runs/detect/angel-r/example-project/train-2/weights/best.engine --source 0   --imgsz 640 --stream --port 8080 --no-save




