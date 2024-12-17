# 合成合理式による流出量計算

- ローカル格納場所

https://drive.google.com/drive/folders/16ZwwPTBiEMIT-1ik91hrJHeYUlIZQcQu?usp=sharing


# 合成合理式

## 基本式
```
Q = 1/3.6 * f * r * A
```

ここで、
- Q: 流出量 (m³/s)
- f: 流出係数
- r: 降雨量 (mm/h)
- A: 流域面積 (km²)

## 流下時間の計算
本プログラムではクラーヘン式を使用:
```
Δt = L / W
```

ここで、
- Δt: 洪水到達時間 (s)
- L: 流量検討地点までの流路の距離 (m) 
  - 流向データからhubenyの式で算出
- W: 洪水伝播速度 (m/s)

## 洪水伝播速度
勾配に応じて以下の値を採用:

| 勾配条件 | 勾配値 | 伝播速度 (m/s) |
|----------|--------|----------------|
| 1/100以上 | slope ≥ 0.01 | 3.5 |
| 1/200以上1/100未満 | 0.005 ≤ slope < 0.01 | 3.0 |
| 1/200未満 | slope < 0.005 | 2.1 |

# 使用方法
1. ファイルの準備・パスの設定
- inputおよびoutputファイルとパスの設定については[config/config.yml]を参照
- inputファイルは緯度経度座標の使用を想定

2. 流域抽出実行ファイルの作成（コンパイル）
- [src/extract_basin]配下のコードをコンパイルして実行ファイルを作成(extract_basin.exe)
以下　gfortranの場合
```bash
cd src/extract_basin

make
```

windowsの場合
- visual studio + iFXを推奨( 参考サイト　)  ソリューションのビルド　＝ コンパイル
- https://computational-sediment-hyd.hatenablog.jp/entry/2022/09/08/194522


3. run.pyの実行
- ルートディレクトリからrun.pyを実行
```bash
python run.py
```



# License
このプロジェクトは主にMITライセンスの下で提供されています。詳細はLICENSE.txtをご覧ください。
ただし、[src/extract_basin]配下のコードについては、原著作者であるKazutake Asahiの著作権が適用されます。

# 修正履歴

241217
- リモートリポジトリの作成
