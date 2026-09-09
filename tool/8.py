from pathlib import Path
import json
import re
import matplotlib.pyplot as plt


def find_key_value(data, key):
    """递归查找 JSON 中指定 key。"""
    if isinstance(data, dict):
        for k, v in data.items():
            if k == key:
                return v

            result = find_key_value(v, key)
            if result is not None:
                return result

    elif isinstance(data, list):
        for item in data:
            result = find_key_value(item, key)
            if result is not None:
                return result

    return None


def natural_sort_key(path: Path):
    """自然排序，例如 2.json 在 10.json 前。"""
    return [
        int(text) if text.isdigit() else text.lower()
        for text in re.split(r"(\d+)", path.name)
    ]


def analyze_values_over_threshold(
    json_dir: str,
    output_dir: str,
    threshold: float = 600.0,
):
    json_root = Path(json_dir)
    save_dir = Path(output_dir)
    save_dir.mkdir(parents=True, exist_ok=True)

    if not json_root.exists():
        print(f"文件夹不存在: {json_root}")
        return

    json_files = sorted(
        json_root.rglob("*.json"),
        key=natural_sort_key
    )

    if not json_files:
        print(f"未找到 JSON 文件: {json_root}")
        return

    # 只保存大于 threshold 的数据
    # 格式：(文件名, fTraceLayerIndex)
    values_over_threshold = []

    for json_file in json_files:
        try:
            with open(json_file, "r", encoding="utf-8-sig") as f:
                data = json.load(f)

            value = find_key_value(data, "fTraceLayerIndex")

            if value is None:
                continue

            value = float(value)

            if value > threshold:
                values_over_threshold.append(
                    (json_file.name, value)
                )

        except Exception as e:
            print(f"读取失败，跳过: {json_file.name}, error={e}")

    if not values_over_threshold:
        print(f"没有找到大于 {threshold} 的 fTraceLayerIndex。")
        return

    # 拆分文件名和值
    file_names = [item[0] for item in values_over_threshold]
    values = [item[1] for item in values_over_threshold]

    print(f"\n大于 {threshold} 的 fTraceLayerIndex 数量: {len(values)}")
    print("大于阈值的数列：")

    for i, (file_name, value) in enumerate(values_over_threshold):
        print(f"[{i}] {file_name}: {value:.3f}")

    # ==================================================
    # 在“大于 threshold 的数列”中计算相邻差值
    # 后一个值 - 前一个值
    # ==================================================
    differences = [
        values[i + 1] - values[i]
        for i in range(len(values) - 1)
    ]

    print("\n相邻两个大于阈值数据的差值：")

    for i, diff in enumerate(differences):
        print(
            f"[{i}] "
            f"{file_names[i]} ({values[i]:.3f})"
            f" -> "
            f"{file_names[i + 1]} ({values[i + 1]:.3f})"
            f", diff = {diff*6.9:.3f}"
        )

    # ==================================================
    # 图1：筛选后大于 threshold 的值
    # ==================================================
    x = list(range(len(values)))

    plt.figure(figsize=(15, 6))
    plt.plot(
        x,
        values,
        marker="o",
        markersize=5,
        linewidth=1.5,
        color="royalblue",
        label=f"fTraceLayerIndex > {threshold}",
    )

    plt.axhline(
        y=threshold,
        color="red",
        linestyle="--",
        linewidth=1.2,
        label=f"threshold = {threshold}",
    )

    plt.xlabel("Filtered sequence index")
    plt.ylabel("fTraceLayerIndex")
    plt.title(f"fTraceLayerIndex Values Greater Than {threshold}")
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.legend()

    if len(file_names) <= 30:
        plt.xticks(x, file_names, rotation=45, ha="right")
    else:
        step = max(1, len(file_names) // 20)
        plt.xticks(
            x[::step],
            file_names[::step],
            rotation=45,
            ha="right"
        )

    plt.tight_layout()

    value_png = save_dir / "trace_layer_index_over_600.png"
    plt.savefig(value_png, dpi=200)
    plt.show()

    print(f"\n大于 {threshold} 的值图已保存: {value_png}")

    # ==================================================
    # 图2：筛选后数列中，相邻两个值的差
    # ==================================================
    if not differences:
        print("大于阈值的数据少于 2 个，无法计算相邻差值。")
        return

    diff_x = list(range(len(differences)))

    plt.figure(figsize=(15, 6))
    plt.plot(
        diff_x,
        differences,
        marker="o",
        markersize=5,
        linewidth=1.5,
        color="darkorange",
        label="next value - previous value",
    )

    plt.axhline(
        y=0,
        color="gray",
        linestyle="--",
        linewidth=1,
    )

    plt.xlabel("Adjacent pair index")
    plt.ylabel("Difference")
    plt.title(
        f"Adjacent Differences in fTraceLayerIndex Sequence > {threshold}"
    )
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.legend()

    # 差值 i 对应 values[i] -> values[i+1]
    if len(differences) <= 20:
        pair_names = [
            f"{file_names[i]}\n→\n{file_names[i + 1]}"
            for i in range(len(differences))
        ]
        plt.xticks(diff_x, pair_names, rotation=45, ha="right", fontsize=8)

    plt.tight_layout()

    diff_png = save_dir / "trace_layer_index_over_600_adjacent_diff.png"
    # plt.savefig(diff_png, dpi=200)
    # plt.show()

    print(f"相邻差值图已保存: {diff_png}")


if __name__ == "__main__":
    analyze_values_over_threshold(
        json_dir=r"E:\CT20260822\Organized_by_Number_Results\00005",
        output_dir=r"C:\Users\Lenovo\Desktop",
        threshold=600.0,
    )
