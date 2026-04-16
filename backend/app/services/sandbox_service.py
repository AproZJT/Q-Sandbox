import asyncio
import time
from collections.abc import AsyncGenerator

import docker
from docker.errors import DockerException

# 启动时初始化 Docker 客户端，连接本地 Docker Desktop
try:
    client = docker.from_env()
except DockerException as e:
    print(f"警告: 无法连接到 Docker 引擎，请确保 Docker Desktop 正在运行。错误: {e}")
    client = None


async def run_sandbox(source_code: str) -> AsyncGenerator[tuple[str, dict], None]:
    """真实的 Docker 安全沙箱引擎"""
    if not client:
        yield "sandbox.result", {
            "exit_code": -1,
            "time_ms": 0,
            "summary": "Docker 引擎未启动",
            "stage": "error",
        }
        return

    yield "sandbox.running", {"message": "正在分配 Docker 隔离容器..."}
    # 稍微暂停一下，让前端把状态渲染出来
    await asyncio.sleep(0.1)

    start_time = time.time()

    # 单行编译运行：将用户代码写入 main.cpp，然后 g++ 编译并执行
    escaped_code = source_code.replace("'", "'\\''")
    command = f"echo '{escaped_code}' > main.cpp && g++ -O2 main.cpp -o main && ./main"

    try:
        # 为了不阻塞 FastAPI 的异步主线程，使用 asyncio.to_thread 跑同步 Docker 调用
        def execute_docker():
            # 拉起容器，执行完毕后自动销毁
            return client.containers.run(
                image="gcc:13",
                command=["sh", "-c", command],
                mem_limit="256m",      # 【安全机制】最大内存 256MB
                network_disabled=True,  # 【安全机制】彻底断网
                remove=True,            # 【安全机制】阅后即焚，不留垃圾
                stdout=True,
                stderr=True,
            )

        logs = await asyncio.to_thread(execute_docker)

        time_ms = int((time.time() - start_time) * 1000)
        output_str = logs.decode("utf-8")

        # 无异常则视为编译和运行成功
        yield "sandbox.stdout", {"chunk": output_str}
        yield "sandbox.result", {
            "exit_code": 0,
            "time_ms": time_ms,
            "summary": "真实沙箱执行完毕，输出正常",
            "stage": "finished",
        }

    except docker.errors.ContainerError as e:
        # Exit Code 非 0（编译失败或运行时错误）
        time_ms = int((time.time() - start_time) * 1000)
        error_output = e.stderr.decode("utf-8") if e.stderr else str(e)

        yield "sandbox.stderr", {"chunk": error_output}
        yield "sandbox.result", {
            "exit_code": e.exit_status,
            "time_ms": time_ms,
            "summary": "代码编译失败或发生运行时错误",
            "stage": "error",
        }
    except Exception as e:
        # 超时或其他系统级异常
        yield "sandbox.stderr", {"chunk": f"沙箱系统异常: {str(e)}"}
        yield "sandbox.result", {
            "exit_code": -1,
            "time_ms": int((time.time() - start_time) * 1000),
            "summary": "沙箱执行超时或崩溃",
            "stage": "error",
        }
