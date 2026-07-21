# 后端启动前的人脸模型准备

如果要启用本地人脸识别，后端启动前需要先准备 InsightFace 模型。

## 本地联调推荐顺序

```powershell
cd D:\PC\Document\HBuilderProjects\campus-system\backend
pip install -r requirements.txt
python scripts/warmup_insightface.py
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 环境变量

本地模型模式：

```env
FACE_PROVIDER=local
FACE_INSIGHTFACE_MODEL=buffalo_l
FACE_INSIGHTFACE_PROVIDERS=CPUExecutionProvider
```

首次运行 `warmup_insightface.py` 时，InsightFace 会下载模型到：

```text
~/.insightface/models/
```

Windows 上一般对应：

```text
C:\Users\<你的用户名>\.insightface\models\
```

## 为什么要预热

不预热也能跑，但第一次调用人脸识别接口时会临时下载和初始化模型，可能出现：

- 第一次请求等待很久
- 网络不好导致接口失败
- 部署到无公网服务器后模型无法自动下载

所以推荐部署或本地演示前先执行：

```powershell
python scripts/warmup_insightface.py
```

看到类似输出即可：

```text
[warmup] initializing InsightFace model: buffalo_l
[warmup] providers: CPUExecutionProvider
[warmup] ready, cache directory: C:\Users\PC\.insightface\models
```

## 服务器无公网时

先在有网络的机器上执行预热脚本，然后把模型目录复制到服务器同一用户目录：

```text
~/.insightface/models/
```

如果后端用 systemd 或 Docker 运行，要注意模型目录属于运行后端的那个用户，不一定是你 SSH 登录的用户。

## 快速自测

已有两张人脸照片时，可以执行：

```powershell
python scripts/test_insightface_local.py start.jpg end.jpg
```

这个命令会实际跑一次人脸提取和相似度比对。
