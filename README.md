# vState-py  
## バーチャルYoutuberのスケジュールをHPから取得してくるモノ。 
## 配信終了時間が書いてないものは、2時間に設定されます。  LIVE配信ではない、動画投稿も、ライブとして扱われます。  正確ではないことをご理解ください。
## ゲリラ配信、HPに記載されてない、twitterでの告知等は、対応していません。
## [いつから.link](https://www.itsukaralink.jp/, "いつから.link"), [ホロジュール](https://schedule.hololive.tv/, "ホロジュール")から取得したデータを時系列にまとめて配信しています。
GET: https[://]vstate-x0y14-dev[.]cf  
* /api/schedule/[past|now|future]/?count=n 
->[{}, {}, {}, ...]   
最後のcountなかったら入ってるもの全部流れてくるのででかい  
* /api/schedule/all  
->{"past": [...], "new": [...], "future": [...]}
