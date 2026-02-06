# use local Spark 4.1.1 (must be set before importing pyspark)
import os
import sys
import platform
import glob
os.environ["SPARK_HOME"] = r"C:\spark-4.1.1-bin-hadoop3"

# import libraries
from pyspark.sql import SparkSession
from pyspark import SparkConf
import time

def _machine_info():
    """Coleta caracteristicas da maquina (cores, memoria) para exibicao."""
    import subprocess
    out = {}
    out["cpu_logical"] = os.cpu_count() or "?"
    # Cores fisicos: Windows (wmic) ou Linux (/proc/cpuinfo)
    out["cpu_physical"] = "?"
    if sys.platform == "win32":
        try:
            r = subprocess.run(
                ["wmic", "cpu", "get", "NumberOfCores,NumberOfLogicalProcessors", "/format:csv"],
                capture_output=True, text=True, timeout=5
            )
            if r.returncode == 0 and r.stdout:
                lines = [l.strip() for l in r.stdout.strip().splitlines() if l.strip() and "Node" not in l]
                total_phys = total_log = 0
                for line in lines:
                    parts = line.split(",")
                    if len(parts) >= 3 and parts[-2].isdigit() and parts[-1].isdigit():
                        total_phys += int(parts[-2])
                        total_log += int(parts[-1])
                if total_phys:
                    out["cpu_physical"] = total_phys
                if total_log:
                    out["cpu_logical"] = total_log
        except Exception:
            pass
        if out.get("cpu_physical") == "?":
            try:
                r = subprocess.run(
                    ["powershell", "-NoProfile", "-Command",
                     "(Get-CimInstance Win32_Processor | Measure-Object -Property NumberOfCores -Sum).Sum; (Get-CimInstance Win32_Processor | Measure-Object -Property NumberOfLogicalProcessors -Sum).Sum"],
                    capture_output=True, text=True, timeout=5
                )
                if r.returncode == 0 and r.stdout:
                    nums = [int(x.strip()) for x in r.stdout.strip().splitlines() if x.strip().isdigit()]
                    if len(nums) >= 2:
                        out["cpu_physical"] = nums[0]
                        out["cpu_logical"] = nums[1]
                    elif len(nums) == 1:
                        out["cpu_physical"] = nums[0]
            except Exception:
                pass
    else:
        try:
            with open("/proc/cpuinfo", "r") as f:
                content = f.read()
            phys = set()
            for block in content.split("\n\n"):
                if "processor" not in block:
                    continue
                core_id = None
                for line in block.splitlines():
                    if line.startswith("core id"):
                        core_id = line.split(":")[-1].strip()
                        break
                if core_id is not None:
                    phys.add(core_id)
            out["cpu_physical"] = len(phys) if phys else (os.cpu_count() or "?")
        except Exception:
            pass
    out["python"] = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    out["sistema"] = f"{platform.system()} {platform.release()}"
    # Memoria: Windows via ctypes
    if sys.platform == "win32":
        try:
            import ctypes
            from ctypes import wintypes
            class MEMORYSTATUSEX(ctypes.Structure):
                _fields_ = [
                    ("dwLength", wintypes.DWORD),
                    ("dwMemoryLoad", wintypes.DWORD),
                    ("ullTotalPhys", ctypes.c_ulonglong),
                    ("ullAvailPhys", ctypes.c_ulonglong),
                    ("ullTotalPageFile", ctypes.c_ulonglong),
                    ("ullAvailPageFile", ctypes.c_ulonglong),
                    ("ullTotalVirtual", ctypes.c_ulonglong),
                    ("ullAvailVirtual", ctypes.c_ulonglong),
                    ("ullAvailExtendedVirtual", ctypes.c_ulonglong),
                ]
            kernel32 = ctypes.windll.kernel32
            m = MEMORYSTATUSEX()
            m.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
            if kernel32.GlobalMemoryStatusEx(ctypes.byref(m)):
                out["mem_total_gb"] = round(m.ullTotalPhys / (1024**3), 2)
                out["mem_avail_gb"] = round(m.ullAvailPhys / (1024**3), 2)
            else:
                out["mem_total_gb"] = out["mem_avail_gb"] = "?"
        except Exception:
            out["mem_total_gb"] = out["mem_avail_gb"] = "?"
    else:
        try:
            with open("/proc/meminfo", "r") as f:
                for line in f:
                    if line.startswith("MemTotal:"):
                        out["mem_total_gb"] = round(int(line.split()[1]) / (1024**2), 2)
                    elif line.startswith("MemAvailable:"):
                        out["mem_avail_gb"] = round(int(line.split()[1]) / (1024**2), 2)
                        break
            if "mem_total_gb" not in out:
                out["mem_total_gb"] = out["mem_avail_gb"] = "?"
        except Exception:
            out["mem_total_gb"] = out["mem_avail_gb"] = "?"
    return out

# main spark program
# init application
if __name__ == '__main__':

    # caracteristicas da maquina (antes do Spark para nao depender da sessao)
    _mi = _machine_info()

    # init session
    # set configs
    # https://spark.apache.org/docs/latest/configuration.html
    # spark's default = spark.sql.files.maxPartitionBytes = 128mb
    # each device & subscription file around [30kb]

    spark = SparkSession \
        .builder \
        .master("local[2]") \
        .appName("small-files-problem") \
        .config("spark.sql.files.maxPartitionBytes", "128mb") \
        .getOrCreate()

    # set log level
    spark.sparkContext.setLogLevel("WARN")

    # show configured parameters (readable)
    _max_partition = next((v for k, v in SparkConf().getAll() if "maxPartitionBytes" in k), "?")
    print("\n" + "=" * 50)
    print("  MAQUINA")
    print("=" * 50)
    print(f"  sistema ....................... {_mi['sistema']}")
    print(f"  CPU (cores fisicos) ........... {_mi.get('cpu_physical', '?')}")
    print(f"  CPU (cores logicos) ........... {_mi['cpu_logical']}")
    print(f"  memoria total ................. {_mi.get('mem_total_gb', '?')} GB")
    print(f"  memoria disponivel ........... {_mi.get('mem_avail_gb', '?')} GB")
    print(f"  Python ....................... {_mi['python']}")
    print("=" * 50)
    print("  CONFIGURACAO SPARK")
    print("=" * 50)
    print(f"  Spark ......................... {spark.version}")
    print(f"  app name ...................... small-files-problem")
    print(f"  master ........................ local[1]")
    print(f"  default parallelism ........... {spark.sparkContext.defaultParallelism}")
    print(f"  max partition bytes ........... {_max_partition}")
    print("=" * 50 + "\n")

    # base path: script directory
    _base = os.path.dirname(os.path.abspath(__file__))
    _device_dir = os.path.join(_base, "files", "device")
    _sub_dir = os.path.join(_base, "files", "subscription")

    # Regra de carregamento: deixe ativa apenas UMA das 3 opcoes abaixo.
    #
    # Regra 1 - 1 arquivo:
    # get_device_file = os.path.join(_device_dir, "device_2022_apr_01.json")
    # get_subscription_file = os.path.join(_sub_dir, "subscription_2022_apr_01.json")
    #
    # Regra 2 - x arquivos (mude 7 para a quantidade desejada):
    # _x = 7
    # _device_list = sorted([f for f in os.listdir(_device_dir) if f.endswith(".json")])[:_x]
    # _sub_list = sorted([f for f in os.listdir(_sub_dir) if f.endswith(".json")])[:_x]
    # get_device_file = [os.path.join(_device_dir, f) for f in _device_list]
    # get_subscription_file = [os.path.join(_sub_dir, f) for f in _sub_list]
    #
    # Regra 3 - todos os arquivos (glob expandido em Python para funcionar no Windows):
    get_device_file = sorted(glob.glob(os.path.join(_device_dir, "*.json")))
    get_subscription_file = sorted(glob.glob(os.path.join(_sub_dir, "*.json")))

    # read device data
    # json file from landing zone
    start = time.time()
    df_device = spark.read \
        .format("json") \
        .option("inferSchema", "true") \
        .option("multiLine", "true") \
        .json(get_device_file)
    _device_count = df_device.count()
    _device_partitions = df_device.rdd.getNumPartitions()
    _device_secs = round(time.time() - start, 2)
    print("  [device]")
    print(f"    registros ...................... {_device_count}")
    print(f"    particoes ..................... {_device_partitions}")
    print(f"    tempo (segundos) .............. {_device_secs}")
    print()

    # read subscription data
    # json file from landing zone
    start = time.time()
    df_subscription = spark.read \
        .format("json") \
        .option("inferSchema", "true") \
        .option("multiLine", "true") \
        .json(get_subscription_file)
    _sub_count = df_subscription.count()
    _sub_partitions = df_subscription.rdd.getNumPartitions()
    _sub_secs = round(time.time() - start, 2)
    print("  [subscription]")
    print(f"    registros ...................... {_sub_count}")
    print(f"    particoes ..................... {_sub_partitions}")
    print(f"    tempo (segundos) .............. {_sub_secs}")
    print()
    _total_secs = round(_device_secs + _sub_secs, 2)
    print("  [resumo]")
    print(f"    tempo total (segundos) ........ {_total_secs}")
    print()
    print("=" * 50)
    print("  CONCLUIDO")
    print("=" * 50 + "\n")

    # stop session
    spark.stop()
