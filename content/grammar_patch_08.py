import json
from pathlib import Path
f=Path('content/grammar.json');d=json.loads(f.read_text(encoding='utf8'))
def put(p,m,form,rows):
 i=next(i for l in d['lessons'] for i in l['items'] if i['pattern']==p)
 i.update(meaning=m,formation=form,usage='Use this pattern in the relationship shown.',register='neutral',nuance='The context controls the strength and attitude.',examples=[{'jp':a,'reading':b,'romaji':c,'en':e} for a,b,c,e in rows],mistake='Check the polarity and required attachment.',comparison='Compare the force and source of information with nearby forms.',question={'prompt':'Choose the expression that fits the sentence.','options':[p,'ために','以来','ばかり'],'answer':p,'explanation':'The context requires the target relationship.'})
R={
'わけにはいかない':('cannot; cannot afford to','V dictionary + わけにはいかない',[('約束したので、行かないわけにはいかない。','やくそくしたので、いかないわけにはいかない。','Yakusoku shita node ikanai wake ni wa ikanai.','I promised, so I cannot not go.'),('明日は試験だから、遊んでいるわけにはいかない。','あしたはしけんだから、あそんでいるわけにはいかない。','Ashita wa shiken da kara asonde iru wake ni wa ikanai.','There is an exam tomorrow, so I cannot keep playing.'),('仕事中に寝るわけにはいかない。','しごとちゅうにねるわけにはいかない。','Shigotochū ni neru wake ni wa ikanai.','I cannot sleep during work.')]),
'しか〜ない':('only; nothing but','N + しか + negative',[('千円しか持っていない。','せんえんしかもっていない。','Sen-en shika motte inai.','I have only 1,000 yen.'),('週末しか会えません。','しゅうまつしかあえません。','Shūmatsu shika aemasen.','I can meet only on weekends.'),('水しか飲まなかった。','みずしかのまなかった。','Mizu shika nomanakatta.','I drank nothing but water.')]),
'決して〜ない':('never; by no means','決して + Vない',[('この秘密を決して話さない。','このひみつをけっしてはなさない。','Kono himitsu o kesshite hanasanai.','I will never tell this secret.'),('彼は決して約束を破らない。','かれはけっしてやくそくをやぶらない。','Kare wa kesshite yakusoku o yaburanai.','He never breaks promises.'),('これは決して簡単ではない。','これはけっしてかんたんではない。','Kore wa kesshite kantan de wa nai.','This is by no means easy.')]),
'ことはない':('there is no need to','V dictionary + ことはない',[('心配することはない。','しんぱいすることはない。','Shinpai suru koto wa nai.','There is no need to worry.'),('急ぐことはありません。','いそぐことはありません。','Isogu koto wa arimasen.','There is no need to hurry.'),('謝ることはないよ。','あやまることはないよ。','Ayamaru koto wa nai yo.','You do not need to apologize.')]),
'そうだ様態':('looks; seems about to','Vます/い-adj stem + そうだ',[('雨が降りそうだ。','あめがふりそうだ。','Ame ga furi-sō da.','It looks like rain.'),('この料理はおいしそうです。','このりょうりはおいしそうです。','Kono ryōri wa oishisō desu.','This dish looks delicious.'),('彼は疲れていそうだ。','かれはつかれていそうだ。','Kare wa tsukarete isō da.','He looks tired.')]),
'そうだ伝聞':('I hear; reportedly','Plain form + そうだ',[('明日は雨だそうです。','あしたはあめだそうです。','Ashita wa ame da sō desu.','I hear it will rain tomorrow.'),('田中さんは来ないそうだ。','たなかさんはこないそうだ。','Tanaka-san wa konai sō da.','I hear Tanaka will not come.'),('この店は有名だそうです。','このみせはゆうめいだそうです。','Kono mise wa yūmei da sō desu.','I hear this shop is famous.')])}
for p,(m,form,rows) in R.items():put(p,m,form,rows)
f.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf8');print('patched',len(R))
