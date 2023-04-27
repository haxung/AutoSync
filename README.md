# 目的

上传/下载 *单个文件夹* 到服务器，便于保存和同步重要文件。

## 环境配置

- 安装 *python3.7*
- 1 台服务器（开启 *ssh* 服务）

# 使用

1. 下载此项目到本地
2. 安装需求的库文件

    ```shell
    py -3 -m pip install requirements.txt 
    ```

3. 配置 `conf.user.json`
4. 运行 *`auto_sync.py`*

    ```shell
    py -3 auto_sync.py
    ```
