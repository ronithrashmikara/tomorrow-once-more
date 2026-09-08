import json
from pathlib import Path

R=[]
def add(title,jp,support,en,notes,questions,romaji=''):
    R.append(dict(id=len(R)+1,title=title,jp=jp,support=support,translation=en,notes=notes,questions=[dict(question=q,answer=a,explanation=e) for q,a,e in questions],romaji=romaji))

add('A morning decision',
'最近、朝はいつも忙しいです。朝ご飯を食べないで出かける日もあります。それで、夜のうちに次の日の準備をすることにしました。かばんに必要な物を入れて、着る服も選びます。明日からは、少し早く起きるつもりです。',
'さいきん、あさはいつもいそがしいです。あさごはんをたべないででかけるひもあります。それで、よるのうちにつぎのひのじゅんびをすることにしました。かばんにひつようなものをいれて、きるふくもえらびます。あしたからは、すこしはやくおきるつもりです。',
'Lately, my mornings are always busy. Some days I go out without eating breakfast. So I decided to prepare for the next day during the evening. I put what I need in my bag and choose my clothes too. Starting tomorrow, I intend to get up a little earlier.',
['最近（さいきん）lately; 準備（じゅんび）preparation; 必要（ひつよう）necessary; 選ぶ（えらぶ）choose.', 'ことにしました presents a personal decision. つもりです expresses an intention. Preview: 夜のうちに means during the evening, before that opportunity ends.'],
[('What two preparations does the writer make?','Packs necessary things and chooses clothes.','Both actions follow the decision to prepare the night before.'),('Has the writer already developed the habit of getting up earlier?','The passage does not establish that.','明日から and つもり describe a future intention.'),('Translate 食べないで出かける.','Go out without eating.','ないで links an omitted action to the action actually performed.')],
'Saikin, asa wa itsumo isogashii desu. Asagohan o tabenaide dekakeru hi mo arimasu. Sorede, yoru no uchi ni tsugi no hi no junbi o suru koto ni shimashita. Kaban ni hitsuyou na mono o irete, kiru fuku mo erabimasu. Ashita kara wa, sukoshi hayaku okiru tsumori desu.')

add('Sharing the housework',
'一人で暮らしていたときは、部屋をあまり片付けませんでした。でも、妹と住むようになってから、毎晩、台所を掃除するようにしています。妹は洗濯をしてくれます。二人で分ければ、家事はそれほど大変ではありません。',
'ひとりでくらしていたときは、へやをあまりかたづけませんでした。でも、いもうととすむようになってから、まいばん、だいどころをそうじするようにしています。いもうとはせんたくをしてくれます。ふたりでわければ、かじはそれほどたいへんではありません。',
'When I lived alone, I did not tidy my room very often. But since I started living with my younger sister, I have made a point of cleaning the kitchen every night. My sister does the laundry for me. If we divide it between us, the housework is not that difficult.',
['暮らす（くらす）live; 片付ける（かたづける）tidy; 台所（だいどころ）kitchen; 家事（かじ）housework.', '住むようになった marks a change in circumstances. 掃除するようにしている describes a deliberate continuing habit. Preview: 分ければ is the conditional of 分ける.'],
[('Who does the laundry?','The younger sister.','妹 is the topic of 洗濯をしてくれます.'),('Which expression means making a continuing effort?','掃除するようにしています.','ようにしている emphasizes an intentional habit.'),('Does the writer say all housework is easy?','No; it is less difficult if they share it.','二人で分ければ states the condition.')],
'Hitori de kurashite ita toki wa, heya o amari katazukemasen deshita. Demo, imouto to sumu you ni natte kara, maiban, daidokoro o souji suru you ni shite imasu. Imouto wa sentaku o shite kuremasu. Futari de wakereba, kaji wa sorehodo taihen dewa arimasen.')

add('A lunch that travels well',
'昼ご飯のお金を節約するために、弁当を作っています。料理は得意ではありませんが、簡単な物なら作れます。今日は野菜を細かく切って、卵と一緒に焼きました。昼までおいしく食べられるように、弁当を涼しい場所に置きます。',
'ひるごはんのおかねをせつやくするために、べんとうをつくっています。りょうりはとくいではありませんが、かんたんなものならつくれます。きょうはやさいをこまかくきって、たまごといっしょにやきました。ひるまでおいしくたべられるように、べんとうをすずしいばしょにおきます。',
'I make a packed lunch to save money on lunch. I am not good at cooking, but I can make simple things. Today I chopped some vegetables finely and cooked them with eggs. I put my lunch in a cool place so that I can still enjoy eating it at lunchtime.',
['節約（せつやく）saving money/resources; 得意（とくい）good at; 細かい（こまかい）fine/small; 焼く（やく）cook with direct/dry heat.', 'するために uses a deliberate action as a purpose. 食べられるように describes a desired possible state. This is a language passage, not food-storage guidance.'],
[('Why does the writer make lunch?','To save money.','The purpose is explicitly marked by ために.'),('What limits the writer’s cooking ability?','They can make simple things, although they are not good at cooking.','なら narrows the claim to 簡単な物.'),('Why is ように natural after 食べられる?','The goal is being able to eat it enjoyably.','A potential form expresses the desired state, rather than a direct chosen action.')],
'Hirugohan no okane o setsuyaku suru tame ni, bentou o tsukutte imasu. Ryouri wa tokui dewa arimasen ga, kantan na mono nara tsukuremasu. Kyou wa yasai o komakaku kitte, tamago to issho ni yakimashita. Hiru made oishiku taberareru you ni, bentou o suzushii basho ni okimasu.')

add('The shopping list',
'買い物に行く前に、冷蔵庫の中を調べておきました。牛乳はまだあったので、買いませんでした。しかし、店で安いお菓子を見つけて、予定よりたくさん買ってしまいました。次からは、必要な物だけをメモしておこうと思います。',
'かいものにいくまえに、れいぞうこのなかをしらべておきました。ぎゅうにゅうはまだあったので、かいませんでした。しかし、みせでやすいおかしをみつけて、よていよりたくさんかってしまいました。つぎからは、ひつようなものだけをメモしておこうとおもいます。',
'Before going shopping, I checked the fridge in advance. There was still milk, so I did not buy any. However, I found cheap sweets at the shop and ended up buying more than planned. Next time, I think I will make a note of only the things I need beforehand.',
['冷蔵庫（れいぞうこ）refrigerator; 調べる（しらべる）check/investigate; 予定（よてい）plan.', 'ておく prepares for a later action. てしまう here conveys an unwanted outcome. おこう is the volitional form of おく.'],
[('What did the writer avoid buying unnecessarily?','Milk.','The fridge check showed there was still some.'),('Which purchase was a problem?','Buying more sweets than planned.','予定よりたくさん and しまいました show the unwanted result.'),('Translate 調べておきました.','I checked it in advance.','おく gives the checking a preparatory purpose.')],
'Kaimono ni iku mae ni, reizouko no naka o shirabete okimashita. Gyuunyuu wa mada atta node, kaimasen deshita. Shikashi, mise de yasui okashi o mitsukete, yotei yori takusan katte shimaimashita. Tsugi kara wa, hitsuyou na mono dake o memo shite okou to omoimasu.')

add('Before the deadline',
'旅行の申し込みは金曜日までです。私は木曜日の夜まで忙しいので、今日のうちに申し込むことにしました。出発する前に、友達と持ち物を確認します。出発の時間を間違えないように、案内のメールも保存しておきます。',
'旅行（りょこう）travel; 申し込み（もうしこみ）application; 今日のうちに（きょうのうちに）before today is over; 出発（しゅっぱつ）departure; 持ち物（もちもの）things to bring; 確認（かくにん）confirmation; 保存（ほぞん）saving/storage.',
'Applications for the trip are open until Friday. I am busy until Thursday night, so I decided to apply today while I have the chance. Before leaving, I will check what to bring with my friend. I will also save the information email so that I do not get the departure time wrong.',
['今日のうちに treats today as a limited opportunity. 前に uses dictionary form 出発する. ないように expresses preventing an unwanted state.','まで is an endpoint; までに would explicitly mark a deadline for completing an action: 金曜日までに申し込む.'],
[('When will the writer apply?','Today.','今日のうちに申し込むことにしました states the decision.'),('Why save the email?','To avoid getting the departure time wrong.','間違えないように supplies the purpose.'),('Complete: 金曜日（まで / までに）申し込んでください。','までに.','The application must be completed by Friday, not continuously performed until Friday.')])

add('A delayed train',
'駅に着いたとき、電車はちょうど出たところでした。次の電車を待っている間に、友達に連絡しました。友達は「急がなくてもいいよ。着いてから、一緒に昼ご飯を食べよう」と言ってくれました。時間があったので、駅の案内を読んでみました。',
'着く（つく）arrive; ちょうど just/exactly; 連絡（れんらく）contact; 急ぐ（いそぐ）hurry; 案内（あんない）information/guidance.',
'When I reached the station, the train had just left. While waiting for the next train, I contacted my friend. My friend kindly said, “You do not have to hurry. Let’s have lunch together after you arrive.” Since I had time, I tried reading the station information.',
['出たところ means the action has just happened. 待っている間に places a shorter event inside an ongoing wait. 着いてから sets an order: arrive, then eat.'],
[('Was the writer on the first train?','No.','It had just departed when the writer arrived.'),('How does the friend respond?','Reassuringly, saying there is no need to hurry.','急がなくてもいい gives permission not to hurry.'),('What does the writer do during the wait?','Contacts the friend and reads station information.','Both are stated after the missed train.')])

add('Choosing a route',
'博物館へ行くなら、駅からバスに乗ると便利です。ただし、日曜日は道が混むので、歩いたほうが早いかもしれません。駅前の地図を見ると、川のそばに短い道があります。雨が降ったら、その道は滑りやすくなるので気を付けてください。',
'博物館（はくぶつかん）museum; 便利（べんり）convenient; 混む（こむ）be crowded; 地図（ちず）map; 滑る（すべる）slip.',
'If you are going to the museum, taking the bus from the station is convenient. However, because the roads are congested on Sundays, walking may be faster. If you look at the map in front of the station, there is a short route beside the river. If it rains, that path becomes slippery, so please be careful.',
['なら offers advice about the topic of going to the museum. と in 地図を見ると introduces what you discover. 降ったら sets the condition for a warning. Preview: verb stem + やすい means easy to do.'],
[('Why might walking be faster on Sunday?','The roads are congested.','The reason is 道が混むので.'),('Which route needs care when it rains?','The short route beside the river.','その道 refers to the path mentioned immediately before.'),('Does the writer promise walking is always faster?','No.','かもしれません expresses possibility, and the suggestion is tied to Sunday.')])

add('A library notice',
'図書館からのお知らせ：本を返すときは、受付までお持ちください。図書館が閉まっていたら、入口の箱に入れてください。ただし、CDは箱に入れないでください。借りた物をなくした場合は、まず電話で相談してください。返す日を延ばしたいなら、期限の前日までに連絡が必要です。',
'受付（うけつけ）reception; 入口（いりぐち）entrance; 場合（ばあい）case; 相談（そうだん）consultation; 延ばす（のばす）extend; 期限（きげん）deadline; 前日（ぜんじつ）previous day.',
'Notice from the library: When returning books, please bring them to reception. If the library is closed, put them in the box at the entrance. However, do not put CDs in the box. If you lose a borrowed item, first consult us by telephone. If you want to extend the return date, you must contact us no later than the day before the deadline.',
['場合は presents an administrative contingency. なら responds to the wish to extend. Preview: お持ちください is the respectful request form of 持つ; learn it as a notice expression here.'],
[('It is closed and you have a CD to return. May you use the box?','No.','The explicit CD exception overrides the general closed-library instruction.'),('What should you do first after losing a borrowed item?','Telephone the library to discuss it.','まず signals the first required step.'),('Can you request an extension on the due date according to this notice?','No; contact is needed by the day before.','期限の前日までに is earlier than the due date itself.')])

add('Learning from a mistake',
'試験の結果がよくなかったのは、勉強する時間が足りなかったからだけではありません。私は答えを覚えるばかりで、理由を考えていませんでした。先生のおかげで、その問題に気が付きました。今は間違えた文をノートに書き、なぜ間違えたのかを説明する練習をしています。',
'結果（けっか）result; 足りる（たりる）be enough; 理由（りゆう）reason; 気が付く（きがつく）notice; 説明（せつめい）explanation.',
'My poor exam result was not only due to insufficient study time. I kept memorizing answers without thinking about the reasons. Thanks to my teacher, I noticed that problem. Now I write the sentences I got wrong in a notebook and practice explaining why I got them wrong.',
['からだけではありません denies an exclusive cause. おかげで attributes a beneficial outcome to someone. Preview: ばかり here means doing little besides one action; のか embeds a question.'],
[('What learning habit was ineffective?','Memorizing answers without considering reasons.','The writer identifies this after rejecting lack of time as the only cause.'),('Is the teacher blamed?','No; the teacher is credited for helping.','おかげで marks a beneficial cause.'),('What is the writer’s new practice?','Explain why the incorrect sentences were wrong.','The final sentence describes analysis, not just memorization.')])

add('A study group',
'勉強会に参加したものの、初めはほとんど話せませんでした。知っている単語でも、会話の中ではすぐに出てこなかったのです。それでも、毎週通ううちに、少しずつ自信がついてきました。間違えても、ほかの人が最後まで聞いてくれるので、安心して話せます。',
'勉強会（べんきょうかい）study group; 参加（さんか）participation; 単語（たんご）word; 通う（かよう）attend regularly; 自信（じしん）confidence; 安心（あんしん）peace of mind.',
'Although I joined a study group, I could hardly speak at first. Even words I knew did not come to mind quickly in conversation. Nevertheless, as I attended each week, I gradually became more confident. Even if I make mistakes, the others listen to the end, so I feel comfortable speaking.',
['ものの introduces a result contrary to what joining might suggest. それでも resumes despite that difficulty. ても accepts a condition without changing the outcome. うちに describes change over a period.'],
[('What problem did the writer have at first?','Known words did not come to mind quickly in conversation.','Knowing a word was not enough for quick spoken retrieval.'),('What helped the writer feel comfortable?','Others listen to the end even when the writer makes mistakes.','聞いてくれる is followed by the reason marker ので.'),('Does ものの here mean because?','No; it means although.','The actual ability to speak contrasts with the expectation after joining.')])

add('Checking an assumption',
'会議は三時に始まるはずでしたが、会議室には誰もいませんでした。予定表を確認すると、開始時間が四時に変わっていました。連絡がなかったわけではありません。私が新しいメールを読んでいなかったのです。それからは、会議の前に必ず予定を確認するようにしています。',
'会議（かいぎ）meeting; 予定表（よていひょう）schedule; 開始（かいし）start; 必ず（かならず）without fail.',
'The meeting was supposed to start at three, but there was nobody in the meeting room. When I checked the schedule, the start time had changed to four. It was not that no notification had been sent. I had not read the new email. Since then, I make sure to check the schedule before meetings.',
['はず was an expectation based on information, not a promise that reality matched it. なかったわけではない denies the explanation “there was no notice.” のです supplies the real explanation.'],
[('When does the meeting actually start?','At four.','The updated schedule provides the corrected time.'),('Who failed to communicate according to the passage?','The passage does not blame the sender; the writer had not read the email.','連絡がなかったわけではありません explicitly rejects no notice.'),('What habit changed?','The writer now always checks the schedule before meetings.','それからは connects the new habit to the incident.')])

add('A workable deadline',
'この仕事は今日中に全部終わるとは限りません。資料の一部がまだ届いていないからです。だからといって、何もしないわけにはいきません。今ある資料だけでできる作業を先に進めます。全部できなくても、午後には途中の結果を報告するつもりです。',
'今日中（きょうじゅう）by the end of today; 資料（しりょう）materials; 一部（いちぶ）part; 届く（とどく）arrive; 作業（さぎょう）task/work; 報告（ほうこく）report.',
'This job will not necessarily be completely finished today, because some of the materials have not arrived yet. Even so, we cannot just do nothing. We will first proceed with work we can do using the materials we have now. Even if we cannot finish everything, we intend to report our interim results in the afternoon.',
['とは限らない denies certainty, not all possibility. わけにはいかない expresses a practical or social constraint. Preview connector: だからといって means that does not mean that.'],
[('Why might completion be delayed?','Some materials have not arrived.','The second sentence explicitly gives the reason.'),('Does the team plan to wait without working?','No; they will proceed with what can be done now.','何もしないわけにはいきません rules out inaction.'),('Translate 今日中に全部終わるとは限りません.','It will not necessarily all be finished today.','It leaves completion possible; it is not a definite statement that completion is impossible.')])

add('Information about a new cafe',
'駅の近くに新しい喫茶店ができたそうです。友達によると、静かで勉強しやすいらしいです。昨日、前を通ると、中に大きな机が見えました。確かに使いやすそうでしたが、席はほとんど空いていませんでした。落ち着いて勉強したいなら、朝早く行ったほうがよさそうです。',
'喫茶店（きっさてん）cafe; 確かに（たしかに）certainly; 席（せき）seat; 空く（あく）be vacant; 落ち着く（おちつく）settle down/be calm.',
'I heard that a new cafe has opened near the station. According to a friend, apparently it is quiet and easy to study in. Yesterday, when I walked past, I could see large tables inside. They certainly looked convenient to use, but almost no seats were free. If you want to study peacefully, going early in the morning seems advisable.',
['できたそうだ reports information. らしい relays an apparently true report. 使いやすそう describes an impression from appearance. よい becomes よさそう, not よいそう, for appearance.'],
[('Which information comes from the friend?','That the cafe is quiet and good for studying.','友達によると marks the source.'),('What did the writer directly observe?','Large tables and very few available seats.','見えました and the following description are direct observations.'),('Why is できたそう different from 使いやすそう?','The first reports an event; the second describes an apparent quality.','Hearsay uses plain form + そう; appearance here uses the adjective stem.')])

add('An unanswered message',
'昨日送ったメッセージに、まだ返事がありません。友達は旅行中なので、電波が弱い場所にいるのかもしれません。前にも山では電話が使えないと言っていました。返事が遅いからといって、私に怒っているとは限りません。明日まで待ってから、もう一度連絡してみます。',
'返事（へんじ）reply; 旅行中（りょこうちゅう）traveling; 電波（でんぱ）radio signal/reception; 弱い（よわい）weak; 怒る（おこる）be angry.',
'There is still no reply to the message I sent yesterday. My friend is traveling, so they may be somewhere with poor reception. They previously said they could not use their phone in the mountains. A slow reply does not necessarily mean they are angry with me. I will wait until tomorrow and then try contacting them again.',
['かもしれない offers one possible explanation. からといって ... とは限らない warns against drawing a firm conclusion from one fact. てみる means try an action and see.'],
[('Is poor reception confirmed?','No; it is a possibility.','かもしれません marks uncertainty.'),('Why does the writer consider that explanation?','The friend is traveling and previously mentioned unusable mountain phone reception.','These details supply supporting context without proving the cause.'),('What will the writer do next?','Wait until tomorrow, then contact the friend again.','まで待ってから fixes the order.')])

add('An opinion in a meeting',
'来月の交流会について、意見を聞かれました。私は「駅に近い会場のほうが、初めて来る人にも分かりやすいと思います」と答えました。一方、同僚は、少し遠くても広い会場を選ぶべきだと言いました。どちらの意見にも理由があるので、参加する人数を調べてから決めることになりました。',
'交流会（こうりゅうかい）social/networking event; 意見（いけん）opinion; 会場（かいじょう）venue; 一方（いっぽう）on the other hand; 同僚（どうりょう）colleague; 人数（にんずう）number of people.',
'I was asked for my opinion about next month’s social event. I answered, “I think a venue close to the station would be easier to find, even for first-time visitors.” On the other hand, a colleague said we should choose a spacious venue even if it was a little far away. Since both opinions had reasons behind them, it was decided to check the number of participants before choosing.',
['と言いました reports an opinion without endorsing it. ことになった presents a group decision. Preview: 聞かれました is passive, “was asked”; べき expresses a recommendation judged proper.'],
[('What does the writer value in a venue?','Ease of finding it, especially for newcomers.','駅に近い and 分かりやすい give the reason.'),('What does the colleague value?','Space.','広い会場 is the colleague’s proposed priority.'),('What must happen before the final choice?','Check the number of participants.','調べてから explicitly sequences the decision.')])

add('Asking for a change',
'田中さんへ。明日の打ち合わせですが、開始を三十分遅らせていただけませんか。午前中に別の用事が入ってしまいました。難しければ、予定どおり始めてください。その場合、先に資料を読んでおくので、後で決まったことを教えていただけると助かります。急なお願いで申し訳ありません。',
'打ち合わせ（うちあわせ）planning meeting; 遅らせる（おくらせる）delay; 用事（ようじ）errand/commitment; 予定どおり（よていどおり）as scheduled; 助かる（たすかる）be helped; 申し訳ありません（もうしわけありません）I apologize.',
'Dear Tanaka, regarding tomorrow’s meeting, could you please delay the start by thirty minutes? Another commitment has come up in the morning. If that is difficult, please start as scheduled. In that case, I will read the materials beforehand, so it would help if you could tell me afterward what was decided. I apologize for the sudden request.',
['ていただけませんか politely requests a favor from the addressee. いただけると助かります frames another request as something helpful. てしまった expresses the inconvenient development.'],
[('Is the delay demanded regardless of the recipient’s situation?','No; the writer permits the original start if changing it is difficult.','難しければ introduces a fallback.'),('If the start time stays the same, what does the writer ask for?','An update afterward about the decisions.','後で決まったことを教えて identifies the requested help.'),('Who is to delay the start in 遅らせていただけませんか?','Tanaka/the recipient.','This is a polite request for the other person’s action, not the writer requesting permission to act.')])

add('Before an appointment',
'来週、初めてこの病院に行きます。案内には、予約した時間の十分前までに受付を済ませなければならないと書いてあります。朝ご飯について分からないことがあったので、病院に電話しました。自分で判断せず、担当の人に確認したほうがいいと思ったからです。持ち物の一覧も送ってもらいました。',
'予約（よやく）appointment; 受付を済ませる（うけつけをすませる）complete check-in; 判断（はんだん）judgment; 担当（たんとう）person in charge; 一覧（いちらん）list.',
'Next week I will go to this hospital for the first time. The instructions say I must finish checking in by ten minutes before my appointment time. I had a question about breakfast, so I phoned the hospital. That was because I thought I should check with the person in charge instead of making my own judgment. I also had them send me a list of things to bring.',
['なければならない expresses a requirement. Preview: 判断せず means without deciding for oneself; ず is a written negative linker, and する becomes せず. てもらう presents receiving help.'],
[('By when must check-in be finished?','Ten minutes before the appointment.','十分前までに marks the completion deadline.'),('Does this passage tell all patients whether they should eat breakfast?','No.','It describes asking the hospital about individual instructions; no universal instruction is given.'),('Why did the writer call?','To clarify an uncertainty with the responsible person.','自分で判断せず contrasts checking with guessing.')])

add('An easier-to-read leaflet',
'祖母は小さい字が読みにくいと言います。そこで、市の運動教室の案内を大きく印刷して渡しました。説明が分かりやすくなっただけでなく、日付も見つけやすくなったそうです。ただ、会場まで一人で行くのは難しいようなので、最初の日は私も一緒に行くことにしました。',
'祖母（そぼ）my grandmother; 運動教室（うんどうきょうしつ）exercise class; 印刷（いんさつ）printing; 渡す（わたす）hand over; 日付（ひづけ）date.',
'My grandmother says small print is hard to read. So I printed the city’s exercise-class leaflet in a larger size and gave it to her. She said the explanations became easier to understand and the dates easier to find as well. However, going to the venue alone seems difficult for her, so I decided to go with her on the first day.',
['Verb stem + にくい/やすい describes difficulty/ease: 読みにくい, 見つけやすい. だけでなく adds a second benefit. ようだ indicates an impression based on circumstances.'],
[('What change did the writer make to the leaflet?','Printed it larger.','大きく印刷して modifies the printing size.'),('Name two benefits reported by the grandmother.','Easier explanations and easier-to-find dates.','The two benefits are connected by だけでなく.'),('Why will the writer accompany her?','Getting to the venue alone seems difficult.','ただ introduces a remaining problem despite the improved leaflet.')])

add('A canceled outdoor event',
'週末、公園で自然について学ぶ会が開かれる予定でした。しかし、前日の夜に強い雨が降り、会は中止されました。参加者には、朝早くメールが送られました。私は出かける前にそれを読んだので、困りませんでした。友達は駅まで行ってから中止を知らされ、少し残念そうでした。',
'自然（しぜん）nature; 開く（ひらく）hold/open; 中止（ちゅうし）cancellation; 参加者（さんかしゃ）participant; 知らせる（しらせる）inform.',
'An event to learn about nature was scheduled to be held in the park at the weekend. However, it rained heavily the night before, and the event was canceled. An email was sent to participants early in the morning. I read it before going out, so I had no trouble. My friend was informed of the cancellation only after reaching the station and looked a little disappointed.',
['開かれる, 中止される and 送られる use passive voice to focus on the event/message. 知らされる is passive of 知らせる, “be informed,” not a causative-passive of 知る.'],
[('Why was the event canceled?','Heavy rain the night before.','The weather precedes the cancellation as its cause.'),('Who avoided an unnecessary journey?','The writer.','The writer read the message before leaving.'),('What does 知らされた mean here?','Was informed.','It is the passive of the verb 知らせる.')])

add('Learning by trying',
'町の清掃活動に子どもたちも参加しました。大人が全部やってしまうのではなく、子どもにもごみの種類を考えさせました。分からないときだけ、大人が説明しました。活動の後、一人の子が「次は家族にも分け方を教えたい」と話していました。無理にやらせるより、自分で試せる機会を作ることが大切だと感じました。',
'清掃（せいそう）cleaning; 種類（しゅるい）type; 分け方（わけかた）way of sorting; 無理に（むりに）by force; 機会（きかい）opportunity.',
'Children also joined the town cleanup. Instead of adults doing everything, we had the children think about the types of rubbish too. Adults explained only when the children did not understand. Afterward, one child said, “Next time I want to teach my family how to sort it too.” I felt it was important to create opportunities for them to try things themselves, rather than force them to do them.',
['考えさせた is causative: had/encouraged them to think. やらせる can mean make or let do; 無理に selects the coercive interpretation. 自分で試せる is potential, “can try for themselves.”'],
[('When did adults explain?','Only when children did not understand.','分からないときだけ limits adult intervention.'),('What did one child want to do next?','Teach their family how to sort rubbish.','The child’s quoted intention supplies the answer.'),('Does every causative necessarily mean forcing someone?','No.','The passage contrasts guided participation with 無理にやらせる, explicitly forcing.')])

add('Help at the community center',
'地域の交流会で、受付を手伝いました。初めて来た方が会場を探していらっしゃったので、入口までご案内しました。その方は「助かりました」と言ってくださいました。私も、準備のときに先輩にいろいろ教えていただきました。人にしてもらってうれしかったことを、今度は自分が誰かにしてあげたいと思います。',
'地域（ちいき）local area; 受付（うけつけ）reception; 先輩（せんぱい）senior/experienced colleague; ご案内する（ごあんないする）humbly guide.',
'I helped at reception for a local social event. A first-time visitor was looking for the venue, so I guided them to the entrance. They kindly said, “That was a help.” I too had received a lot of advice from a more experienced colleague during the preparations. Next time, I would like to do something for someone else that I was happy to have someone do for me.',
['いらっしゃる honors the visitor; ご案内する humbles the writer’s action toward the visitor. くださる describes a respected person giving; いただく describes humbly receiving. あげたい here is a private intention, not a phrase to announce to a superior.'],
[('Who is honored by 探していらっしゃった?','The visitor.','The subject of the searching action is the first-time visitor.'),('Who received teaching from a senior?','The writer.','教えていただきました describes the writer humbly receiving a favor.'),('What is the writer’s broader intention?','Pass on the help they have appreciated to someone else.','The final sentence connects receiving and giving support.')])

add('Comparing two services',
'市の自転車サービスには、一日券と月間券があります。一日券は一回だけ使う人に向いています。一方、月間券は値段が高い代わりに、何度でも利用できます。職場が近ければ近いほど、自転車で通う負担は小さくなります。私は毎日使うわけではないので、しばらく一日券で様子を見るつもりです。',
'一日券（いちにちけん）one-day pass; 月間券（げっかんけん）monthly pass; 向く（むく）suit; 負担（ふたん）burden; 様子を見る（ようすをみる）see how things go.',
'The city’s bicycle service has day passes and monthly passes. A day pass suits someone using the service just once. A monthly pass, on the other hand, is more expensive but allows unlimited use. The closer your workplace is, the less burdensome cycling there is. Since I do not use it every day, I intend to try day passes for a while and see how it goes.',
['代わりに balances a disadvantage and benefit. 近ければ近いほど expresses a linked scale: the closer, the less burden. 毎日使うわけではない denies daily use, not all use.'],
[('Which pass allows repeated use?','The monthly pass.','何度でも利用できます states the benefit.'),('Why does the writer choose day passes for now?','They do not use the service every day.','The writer bases the choice on actual frequency.'),('Does 代わりに mean someone acts as a substitute here?','No; it expresses a tradeoff.','Higher price is balanced by more use.')])

add('Read beyond the headline',
'ニュースの見出しだけを読んで、内容が全部分かったと思ってしまうことがあります。しかし、短い見出しには、必要な情報がすべて入っているわけではありません。例えば「料金が半額に」という見出しでも、対象が学生だけという場合があります。得をするのは誰なのか、いつまでなのかという条件こそ、本文で確かめるべきです。',
'見出し（みだし）headline; 半額（はんがく）half price; 対象（たいしょう）eligible target/group; 得をする（とくをする）benefit/save money; 条件（じょうけん）condition; 本文（ほんぶん）main text.',
'Sometimes we read only a headline and end up thinking we understand the whole story. However, a short headline does not necessarily contain all the information we need. For example, even a headline saying “Half-price fees” may apply only to students. The conditions - who benefits and until when - are precisely what we should check in the main text.',
['だけ limits what was read; わけではない qualifies the claim about completeness. こそ emphasizes the conditions as the crucial focus. べき presents advice the writer considers proper.'],
[('What is the main warning?','A headline can omit important conditions.','The student-only discount illustrates missing qualifications.'),('In the example, must every reader receive half price?','No; eligibility may be limited to students.','対象が学生だけ is an explicit possible restriction.'),('What does 条件こそ emphasize?','The conditions are exactly what deserves checking.','こそ highlights rather than merely limits the noun.')])

add('A practical guide to an app',
'新しい連絡アプリでは、写真だけでなく、短い音声も送れます。使い方は難しくありません。まず相手を選び、次に送りたい物を選びます。例えば、場所を説明するときは、地図の画像などを送ると便利です。ただし、住所や電話番号などの個人情報を送る前には、相手をもう一度確認してください。便利だからといって、確認を省いてよいわけではありません。',
'音声（おんせい）audio; 画像（がぞう）image; 個人情報（こじんじょうほう）personal information; 省く（はぶく）omit.',
'With the new messaging app, you can send not only photos but also short audio messages. It is not difficult to use. First select the recipient, and then choose what to send. For example, when explaining a location, it is useful to send something such as a map image. However, before sending personal information such as an address or phone number, check the recipient once more. Convenience does not mean it is fine to skip checking.',
['だけでなく ... も adds another function. など offers non-exhaustive examples. からといって ... わけではない rejects an unjustified conclusion.'],
[('What must be selected first?','The recipient.','まず identifies the first step.'),('Are addresses and phone numbers an exhaustive list of personal information?','No.','など marks examples, not a complete inventory.'),('What conclusion does the writer reject?','That convenience makes checking unnecessary.','The last sentence explicitly rejects skipping verification.')])

add('A change at work',
'働き方の変更について、会社から説明がありました。来月から、週に一度、家で仕事をしてもよいそうです。この制度に関して不明な点がある場合は、担当者に質問できます。私は通勤時間が減ることに期待していますが、家で集中できるかどうかは、実際に試してみないと分かりません。新しい制度をうまく使うには、仕事の進め方も見直す必要があると思います。',
'制度（せいど）system/policy; 不明（ふめい）unclear; 担当者（たんとうしゃ）person responsible; 期待（きたい）expectation; 集中（しゅうちゅう）concentration; 見直す（みなおす）reconsider/review.',
'The company explained a change to working arrangements. Apparently, starting next month we may work from home once a week. Anyone with questions about this policy can ask the person responsible. I look forward to less commuting, but I will not know whether I can concentrate at home unless I actually try it. I think making good use of the new policy also requires reviewing how we carry out our work.',
['について and に関して both introduce a topic; に関して suits a formal explanation. かどうか embeds whether. 試してみないと分からない makes trying a necessary condition for knowing.'],
[('How often is home working allowed?','Once a week.','週に一度 specifies the frequency.'),('What remains uncertain for the writer?','Whether they can concentrate at home.','かどうか introduces the unresolved question.'),('What else may need to change besides work location?','The way work is organized/carried out.','仕事の進め方も expands the required review.')])

add('Choosing by conditions',
'旅行の費用は、泊まる場所や時期によって大きく変わります。同じホテルでも、週末は平日より高くなることがあります。私たちは安さだけで決めず、駅からの距離や食事の有無も比べました。その結果、少し高くても朝食付きの宿を選びました。朝、店を探す時間がいらないので、そのほうが私たちの予定に合っていたのです。',
'費用（ひよう）cost; 時期（じき）time/season; 距離（きょり）distance; 有無（うむ）presence or absence; 朝食付き（ちょうしょくつき）breakfast included; 宿（やど）lodging.',
'Travel costs vary considerably according to where and when you stay. Even the same hotel may cost more at weekends than on weekdays. We did not decide by price alone, but also compared distance from the station and whether meals were included. As a result, we chose lodging with breakfast even though it cost a little more. We did not need to spend time looking for a place in the morning, so that suited our plans better.',
['によって marks the factors on which costs depend. ことがある expresses occasional occurrence. 安さ nominalizes 安い. そのほう refers to choosing breakfast-inclusive lodging.'],
[('Name two factors affecting the price.','Place of stay and time/season.','場所や時期によって names both.'),('Did the travelers choose the cheapest option automatically?','No.','安さだけで決めず explicitly rejects that approach.'),('Why was breakfast inclusion worth the extra cost to them?','It saved the time needed to find a place to eat.','The benefit fit their particular schedule.')])

add('A habit that grows',
'日本語の日記を書き始めたころは、一日に二文しか書けませんでした。知らない表現を調べながら書くので、時間もかかりました。それでも続けているうちに、同じ言い方を何度も使っていることに気が付きました。そこで、前の日記を読み返し、少し違う表現に変えてみました。最近は、書ける内容が広がってきたと感じます。これからも、長さより分かりやすさを大切にしていきたいです。',
'表現（ひょうげん）expression; 読み返す（よみかえす）reread; 広がる（ひろがる）expand; 長さ（ながさ）length.',
'When I started writing a Japanese diary, I could write only two sentences a day. Writing while looking up unfamiliar expressions also took time. Still, as I kept going, I noticed I was using the same expressions repeatedly. So I reread earlier entries and tried changing them to slightly different expressions. Recently, I feel the range of things I can write has expanded. I want to keep valuing clarity more than length.',
['書き始める focuses on starting; ながら links simultaneous actions by the same person. てきた traces change up to now, whereas ていきたい looks forward from now. しか needs a negative predicate.'],
[('What did rereading reveal?','Repeated use of the same expressions.','The writer noticed this while continuing the diary.'),('Does しか書けません mean the writer wrote no sentences?','No; only two per day.','二文 supplies the limited positive amount.'),('What is the writer’s future priority?','Clarity rather than length.','長さより分かりやすさ states the preference.')])

add('When silence is misleading',
'新しいクラスでは、静かな人は話したくないのだと思いがちです。私も隣の人にあまり声をかけていませんでした。ところが、ある日、一緒に帰る機会があり、話してみると、共通の趣味がたくさんありました。その人は「自分から話しかけるのが苦手なだけなんです」と言いました。見た様子だけで相手の気持ちを決めつけないようにしたいと思いました。',
'隣（となり）next to; 声をかける（こえをかける）speak to; 共通（きょうつう）shared; 趣味（しゅみ）hobby; 苦手（にがて）not good at; 決めつける（きめつける）assume dogmatically.',
'In a new class, we tend to think quiet people do not want to talk. I too had rarely spoken to the person next to me. However, one day we had a chance to go home together, and when I tried talking, we had many hobbies in common. They said, “I am simply not good at starting conversations.” I decided I wanted to avoid judging another person’s feelings by appearances alone.',
['がち expresses a tendency, often one viewed critically. ところが introduces an unexpected turn. だけなんです narrows the explanation to one issue, while ないようにしたい expresses an intended precaution.'],
[('What assumption did the writer initially make?','Quiet people probably do not want to talk.','The first sentence describes the tendency that influenced the writer.'),('What was the classmate’s actual difficulty?','Starting a conversation themselves.','自分から話しかけるのが苦手 is the classmate’s explanation.'),('What lesson does the writer draw?','Avoid deciding feelings solely from outward behavior.','The final sentence states the new intention.')])

add('Trying before buying',
'新しい机を買おうと思って店に行きました。写真ではちょうどよい大きさに見えましたが、実物は思ったより大きく感じられました。店員に相談したところ、小さい型もあると教えてもらいました。すぐに買おうとせず、まず家の部屋を測ってみることにしました。気に入った物を見つけると急いで決めたくなりますが、長く使う物こそ、落ち着いて選ぶ必要があります。',
'実物（じつぶつ）actual object; 型（かた）model/type; 測る（はかる）measure; 気に入る（きにいる）take a liking to.',
'I went to the shop intending to buy a new desk. In the photo it looked just the right size, but the actual desk felt bigger than I expected. When I consulted a shop assistant, they told me a smaller model was also available. Instead of trying to buy it immediately, I decided to measure my room first. When we find something we like, we want to decide quickly, but things we will use for a long time are precisely what need careful selection.',
['買おうと思う expresses intention; 買おうとする focuses on an attempt or imminent action. たところ here reports the result of trying something, not merely the moment just after it. 測ってみる is an exploratory action.'],
[('How did the real desk differ from the photo impression?','It felt larger than expected.','思ったより大きく contrasts the actual impression with expectation.'),('What will the writer do before buying?','Measure the room.','まず and ことにしました identify the new plan.'),('What does 相談したところ introduce?','The result of the consultation: learning about a smaller model.','This use of ところ presents an outcome after acting.')])

add('What practice means',
'外国語が上手な人でも、初めから何でも話せたわけではないでしょう。間違えた経験があるからこそ、相手が分かりやすい言い方を考えられるのだと思います。私も以前は、間違えることは恥ずかしいことだと考えていました。しかし今は、間違いに気が付くこと自体が、前に進むための大切な一歩なのだと感じます。同じ失敗を繰り返さない工夫は必要ですが、失敗を一度もしないことを目標にすると、話す機会まで失ってしまいます。',
'恥ずかしい（はずかしい）embarrassing; 自体（じたい）itself; 一歩（いっぽ）one step; 繰り返す（くりかえす）repeat; 工夫（くふう）devising/improvement; 目標（もくひょう）goal; 失う（うしなう）lose.',
'Even people skilled in a foreign language probably could not say everything from the beginning. I think it is precisely because they have experience making mistakes that they can consider ways of speaking that are clear to others. I too used to think making mistakes was embarrassing. Now, though, I feel that noticing a mistake is itself an important step forward. We need ways to avoid repeating the same errors, but if our goal is never to make even one mistake, we end up losing opportunities to speak.',
['こと turns a clause into a concept that can be discussed. からこそ emphasizes a productive cause. まで after 話す機会 indicates even that opportunity is lost. わけではない qualifies an overbroad assumption.'],
[('Does the writer say errors should be repeated without reflection?','No.','同じ失敗を繰り返さない工夫は必要 explicitly calls for improvement.'),('What risk comes from aiming for zero mistakes?','Losing opportunities to speak.','The final conditional connects the goal to avoidance.'),('Summarize the main argument in one sentence.','Mistakes, when noticed and used to improve, are part of progress, so perfection should not prevent practice.','A complete summary includes both learning from errors and continuing to communicate.')])

add('A community proposal',
'町の図書館をもっと長い時間開けてほしいという意見が出ています。仕事の後に利用したい人にとっては、今の閉館時間は早すぎるからです。一方、時間を延ばすには、人員や費用を増やさなければなりません。そこで、まず週に一日だけ遅くまで開け、利用する人の数を調べることになりました。つまり、すぐに毎日変えるのではなく、小さく試してから判断するということです。ただし、人数だけでは利用者の満足度までは分かりません。そのため、短いアンケートも行う予定です。',
'閉館（へいかん）closing a facility; 人員（じんいん）staffing; 利用者（りようしゃ）user; 満足度（まんぞくど）satisfaction level; アンケート questionnaire.',
'People have proposed keeping the town library open longer. This is because the current closing time is too early for those who want to use it after work. On the other hand, extending the hours requires more staff and money. So it was decided to start by keeping it open late just one day a week and counting users. In other words, instead of immediately changing every day, the plan is to make a small trial and then decide. However, numbers alone do not reveal users’ level of satisfaction. Therefore, a short questionnaire is also planned.',
['一方 contrasts perspectives; そこで introduces a response to the problem; つまり restates its meaning; ただし adds a qualification; そのため introduces the resulting action. にとって identifies the group from whose perspective a judgment holds.'],
[('Why not extend every day immediately?','More hours require more staffing and money, so a limited trial is planned first.','The proposal responds to the resource constraint.'),('What extra information will the questionnaire seek?','Users’ satisfaction, which a head count alone does not reveal.','人数だけでは ... 満足度までは分かりません states the information gap.'),('Replace つまり with an English discourse phrase.','In other words.','The following sentence restates the trial strategy rather than adding an unrelated result.')])

add('A sustainable way to study',
'日本語の学習を続けるには、予定を立てるだけでは十分ではありません。予定どおりに進まなかったとき、どう調整するかも考えておく必要があります。私も最初は、毎日新しい単語をたくさん覚えようとしていました。しかし、前に習った言葉を復習する時間がなくなり、見たことがあるのに意味が思い出せない言葉が増えていきました。そこで、新しい内容を減らす代わりに、短い復習を毎日入れました。週末には、知らない文章を読み、覚えた表現がどう使われているかを確かめています。知っている項目の数は学習の目安にはなりますが、それだけで使える力があるとは言えません。大切なのは、自分の弱い部分を見つけ、それに合った練習を選ぶことだと思います。忙しい日は十分しか勉強できないこともあります。それでも、やめてしまうより、短くても思い出す機会を作るほうが、私には続けやすいのです。',
'調整（ちょうせい）adjustment; 復習（ふくしゅう）review; 項目（こうもく）item; 目安（めやす）rough guide; 弱い部分（よわいぶぶん）weak area; 十分（じゅっぷん）ten minutes in the final paragraph, contrasted with 十分（じゅうぶん）sufficient near the beginning.',
'Continuing to learn Japanese takes more than making a plan. You also need to think ahead about how to adjust when things do not go as planned. At first, I too tried to memorize many new words every day. But I ran out of time to review earlier vocabulary, and more and more words looked familiar without my being able to recall their meanings. So I reduced new content in exchange for including a short review every day. At weekends I read unfamiliar passages and check how expressions I have learned are used. The number of items you know can be a rough measure of study, but that alone does not establish usable ability. I think what matters is finding your weak areas and choosing practice that fits them. On busy days, sometimes I can study for only ten minutes. Even so, creating an opportunity to recall things, however brief, is easier for me to sustain than stopping altogether.',
['には makes continued learning the goal/topic; ておく anticipates later difficulties. 代わりに expresses a tradeoff in study time. とは言えない rejects a conclusion that the evidence does not justify. しか requires the negative できない. Notice how the writer moves from problem to change, evidence, and qualified conclusion.'],
[('What caused the growing recall problem?','Too much new vocabulary left no time to review earlier words.','The cause is the imbalance described in the opening personal example.'),('What does the writer do at weekends, and why?','Read unfamiliar passages to check how learned expressions are used.','The purpose goes beyond remembering isolated meanings.'),('Which statement best matches the writer: A learn as many items as possible; B never change the plan; C adapt practice to weak areas and keep retrieving regularly; D stop when time is short?','C.','A repeats the original problem, B ignores adjustment, and D contradicts the final paragraph.'),('Read the two uses of 十分 and give their meanings.','じゅうぶん: sufficient; じゅっぷん: ten minutes.','The first describes adequacy; the second is a duration before しか. じっぷん is another accepted pronunciation of ten minutes.')])

Path(__file__).with_name('readings.json').write_text(json.dumps({'lessons':R},ensure_ascii=False,indent=2),encoding='utf-8')
