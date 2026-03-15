# aubo-robot-setup
```bash
git clone --recurse-submodules git@github.com:harrisonseby/aubo-robot-setup.git
```
```bash
git submodule update --init --recursive
```

```bash
ros2 launch aubo_examples aubo.launch.py use_fake_hardware:=true # set this to false to run on real hardware
```