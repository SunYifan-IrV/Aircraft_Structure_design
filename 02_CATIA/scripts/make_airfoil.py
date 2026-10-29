#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
把 UIUC 翼型 .dat（Selig 格式）转成 CATIA 可读的"闭合环"点文件 (x, y 归一化)。
运行： python make_airfoil.py
输出： ../airfoil/fx63137_loop.csv, ../airfoil/e387_loop.csv
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
AIR = os.path.join(HERE, "..", "airfoil")


def _parse(path):
    """解析 Selig 格式坐标：只保留归一化弦向坐标 0<=x<=1 的行（自动排除名称行与'49.0 49.0'计数行）。"""
    pts = []
    with open(path) as f:
        for line in f:
            t = line.split()
            if len(t) == 2:
                try:
                    x, y = float(t[0]), float(t[1])
                except ValueError:
                    continue
                if 0.0 <= x <= 1.0001:
                    pts.append((x, y))
    return pts


def read_fx63137():
    """FX 63-137: 上表面(LE->TE) 49 点 + 下表面(LE->TE) 49 点"""
    path = os.path.join(AIR, "fx63137.dat")
    pts = _parse(path)
    # 前 49 点 = 上表面, 后 49 点 = 下表面
    upper = pts[:49]
    lower = pts[49:]
    # 唯一点闭合环：TE -> 上表面逆序 -> LE -> 下表面 -> (去掉末尾重复 TE)
    # 首点 TE(1,0)，末点不再重复 TE，闭合交由 CATIA 的 SetClosing 完成
    loop = [upper[-1]] + upper[-2:0:-1] + lower[:-1]
    return loop


def read_e387():
    """E387: 已是单闭合环 (TE -> 上表面逆 -> LE -> 下表面 -> TE)；去掉末尾重复 TE"""
    path = os.path.join(AIR, "e387.dat")
    return _parse(path)[:-1]


def write_csv(name, pts):
    path = os.path.join(AIR, name)
    with open(path, "w") as f:
        f.write("# x,y (normalized chord=1), closed loop\n")
        for x, y in pts:
            f.write(f"{x:.6f},{y:.6f}\n")
    print(f"wrote {path}  ({len(pts)} points)")


if __name__ == "__main__":
    write_csv("fx63137_loop.csv", read_fx63137())
    write_csv("e387_loop.csv", read_e387())
