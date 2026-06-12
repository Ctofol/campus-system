"""
本地测试 InsightFace 起止比对：
  python scripts/test_insightface_local.py 起跑.jpg 结束.jpg
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.face_local_insightface import compare_two_images, similarity_to_display_score


def main():
    if len(sys.argv) < 3:
        print("用法: python scripts/test_insightface_local.py <start.jpg> <end.jpg>")
        sys.exit(1)
    sim, err = compare_two_images(sys.argv[1], sys.argv[2])
    if sim is None:
        print("失败:", err)
        sys.exit(2)
    print(f"余弦相似度: {sim:.4f}")
    print(f"展示分数(0-100): {similarity_to_display_score(sim)}")
    print("通过" if sim >= 0.42 else "未通过（可调 FACE_LOCAL_MIN_SIMILARITY）")


if __name__ == "__main__":
    main()
