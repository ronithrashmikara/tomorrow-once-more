from pathlib import Path
import json,re,html
ROOT=Path(__file__).resolve().parent
ROOT.mkdir(exist_ok=True)
PROMPT='''Create an original 7 hour 30 minute Japanese learning drama, titled もういちど、あした / Tomorrow, Once More. Deliver a polished PDF with an accurate contents page, bookmarks, page numbers, an editable screenplay, and a machine-readable grammar coverage ledger.

AUDIENCE AND LANGUAGE
The learner knows common beginner vocabulary but starts with almost no grammar. All Japanese must contain hiragana and katakana only, plus punctuation and Arabic digits where helpful. No kanji, even in names, scene headings, props, examples, captions, glossaries, or credits. Use light phrase spacing for beginners. Do not use romaji as a substitute for Japanese. Show each Japanese dialogue line followed immediately by its faithful, natural English translation. All in-world speech is Japanese; English is a parallel reading track, not something actors speak. Translate important scene descriptions and on-screen text too. Explain grammar in English. Distinguish contextual translations from literal structure when they differ.

STORY
An original contemporary Japanese rebirth mystery with an adult female protagonist, emotional stakes, humor, friendships, family conflict, earned romance, and fair-play clues. Aoi, 22, wakes up one year before her mother's neighborhood cafe was destroyed by a forged transaction and a staged theft. Her memories are incomplete. She cannot solve the mystery by magical knowledge alone. Saving someone she distrusted changes the timeline and makes later memories unreliable. Use rebirth/revenge conventions, but copy no existing characters, dialogue, scenes, or distinctive plot. No superhuman heroine, convenient confession, or villain who explains the entire scheme. Each scene needs a concrete desire, obstacle, decision, and consequence. Seed every reveal in an earlier visible or audible detail. Give the heroine meaningful agency and flawed assumptions.

STRUCTURE
450 minutes total: 90 scenes with target runtimes averaging five minutes, grouped into nine 50-minute chapters. The first 60 minutes form a complete opening movement with a partial victory and a consequential cliffhanger. Begin immediately with a mystery that can be understood through very simple Japanese and visual storytelling. Start with identity, possession, questions, demonstratives, location, numbers and time; then existence, movement, action, description and polite past. Expand through the remaining N5 structures, then N4. Do not begin with an advanced exposition monologue. Casual fragments and fixed greetings may appear early if glossed. Naturalness matters: avoid repeating pronouns and names unnecessarily, and use polite speech when context supports it. Teach casual forms before sustained intimate or confrontational casual dialogue.

GRAMMAR AUDIT
There is no official exhaustive JLPT grammar inventory. Build a comprehensive, explicitly unofficial N5-N4 syllabus using multiple public study references plus official JLPT level descriptions. Do not copy proprietary example sentences or explanations. Define the scope and how variants are counted. Give each item a stable ID, kana pattern, original English explanation, original kana example and translation, prerequisites, first scene, and at least two later reuse scenes. Separate core items from disputed level placements, bridge forms, and fixed expressions. Include conjugation rules and irregulars, particles and contrasts, tense/polarity, adjectives, noun modification, counters, comparisons, aspect, conditionals, giving/receiving, intention, ability, reported speech, requests, obligations, prohibitions, experience, passive, causative, and introductory honorific/humble forms. Never claim guaranteed exam completeness. Audit coverage across the entire finished script; planned coverage is not evidence of actual usage.

SCENE FORMAT
Scene ID; cumulative target start/end; kana and English title; location/time; cast; emotional goal; grammar IDs introduced and recycled; bilingual action blocks; unique line IDs; speaker in kana; Japanese dialogue; English translation. Add performance direction only where useful. Keep explanations outside the dramatic dialogue. After each scene give 2-4 short English grammar notes tied to actual line IDs, two comprehension questions with answers, and one short optional speaking exercise. Exercises are outside film runtime. Limit unfamiliar vocabulary, gloss essential plot words, and reintroduce them naturally.

TIMING AND PRODUCTION
Write enough material for the duration. Count spoken Japanese mora or kana characters, estimate at an explicitly stated natural beginner-friendly rate, and separately budget motivated action, reactions and transitions. Do not count English translations or exercises as Japanese film dialogue. Do not stretch a short script with blank pauses, repeated footage, arbitrary timestamps, or unrelated montages. Label screenplay timings as estimates until a performed read-through or synthesized dialogue verifies them. Once audio exists, measure actual durations and revise the edit. Preserve voice identity, wardrobe, geography, prop continuity, eyelines, and clue visibility. Create short shot-level generation prompts; do not send an hour-long screenplay to a short-clip model.

DELIVERY AND QUALITY GATES
Deliver (1) story bible and nine-chapter plot, (2) complete scoped grammar inventory and progression, (3) full script in sequential batches, (4) bilingual contents with real page numbers, (5) character/clue/timeline continuity ledger, (6) grammar coverage with actual line references, and (7) shot manifest plus honest cost/run report. First deliver the opening-hour draft and its audit. Check every Japanese field for kanji. Review particles, transitivity, conjugation, register, translation fidelity and speaker intent. Render sample and dense PDF pages to inspect fonts, clipping and spacing. Do not assert native-speaker review unless performed.

COMPUTE CONSTRAINT
Total authorized Modal budget: USD 30, including setup, CPU, GPU, memory, storage and retries. Modal credits do not pay another provider's hosted API fees. Verify current weights, licenses, implementation and hardware needs. Prefer the verified H3 Turbo/fast inference route when compatible. Pin tested versions. Keep credentials out of scripts, PDFs and logs. Benchmark a tiny representative clip first, account for startup, reserve a safety margin and stop if projected full production exceeds the remaining budget. Record actual generation time and measured media duration. No persistent warm GPU, unlimited retries, public unauthenticated endpoint, or silent model substitution. If the requested full video cannot fit, deliver completed artifacts and the exact benchmark/blocker; ask before changing the product to a slideshow or a different model.
'''

# Original editorial inventory. A row is a teaching unit; related variants share a row.
GROUPS=[
('N5 foundations',1,'''です|Noun predicates; polite identity
じゃありません / ではありません|Negative noun predicates
でした / じゃありませんでした|Past noun predicates
は|Topic and contrast; pronounced wa
か|Polite question marker
の|Possession and noun linkage
も|Also; replaces topic or subject markers
これ / それ / あれ / どれ|Independent demonstratives
この / その / あの / どの|Demonstratives before nouns
ここ / そこ / あそこ / どこ|Places
こちら / そちら / あちら / どちら|Polite directions and alternatives
だれ / なに / なん|People and things; sound-dependent readings
と|Complete noun list and accompaniment
ね / よ|Shared confirmation and new information
はい / いいえ|Responses; align with proposition and context
いくつ / いくら|Number of things and price
じ / ふん / はん|Clock time and irregular readings
に|Specific time; some time words take no particle
から / まで|Starting and ending points
や / など|Non-exhaustive lists'''),
('N5 everyday action',2,'''が|Subject, new information and question-word subjects
あります / います|Existence; things versus animate beings
に ... が あります|Location of existence
うえ / した / なか / そと / まえ / うしろ / となり / あいだ|Relative position with の
ます / ません|Polite nonpast affirmative and negative
ました / ませんでした|Polite past affirmative and negative
を|Direct object; pronounced o
で|Place of action and means
へ / に|Direction and destination
と いっしょに|Together with
いつ / どう / どうして|Time, manner and reason questions
あまり ... ません / ぜんぜん ... ません|Low or zero frequency/degree in beginner usage
いつも / よく / ときどき|Frequency words and placement
だけ|Only; limitation
ぐらい / くらい|Approximate quantities
ひとつ / ふたつ / みっつ|General counter series
ひとり / ふたり / にん|People counters
まい / ほん / さつ / ひき / かい|Counter agreement and sound changes
まいにち / しゅうに ... かい|Frequency over a time interval
じかん / かげつ / ねん|Duration, contrasted with clock time'''),
('N5 descriptions and choices',3,'''い adjective|Present affirmative and attributive use
くない / くありません|Negative い adjectives; いい becomes よくない
かった / くなかった|Past い adjectives; いい becomes よかった
な adjective|Predicate versus な before a noun
な adjective tense/polarity|Copular conjugations
くて / で|Linking adjective descriptions
く / に|Adverbial adjective forms
すき / きらい / じょうず / へた|Preferences and skills with が
ほしい|Wanting a thing; normally one's own desire
たい|Verb stem plus desire; adjective-like conjugation
より|Comparison standard
の ほうが|Preference or comparative side
ほど ... ない|Not as ... as
の なかで ... が いちばん|Superlative in a set
どちら / どっち|Choosing between two
ませんか|Polite invitation
ましょう / ましょうか|Proposal and offer
に いきます|Verb stem plus purpose of movement
から|Reason clause; distinguish from starting-point から
が / でも|Contrast and conversational softening'''),
('N5 verb foundations',4,'''dictionary form|Three verb groups and irregular する / くる
ない form|Negative plain verbs and irregular ない / こない
た form|Plain past and sound changes
て form|Conjugation sound changes; いく becomes いって
て ください|Positive request
ないで ください|Negative request
て います|Ongoing action; common resulting states
て も いい|Permission
て は いけません|Prohibition
て ... て|Ordered or linked actions
て から|After completing an action
まえに|Before noun/verb event; dictionary form
あとで|After noun/verb event; た form
とき|Time clauses; tense changes interpretation
もう / まだ|Already and still; まだ ... ていません
plain noun/adjective predicates|だ / だった / じゃない and register
relative clauses|Plain clause before a noun without a relative pronoun
の / こと|Nominalizing actions
ことが できます|Ability using dictionary form
なければ なりません|Obligation
なくても いい|Lack of necessity
でしょう|Tentative judgment; intonation and context'''),
('N4 plans and experience',5,'''た ことが あります|Past experience; not a single dated event
たり ... たり します|Representative actions
つもりです|Intention; affirmative and negative
よていです|Scheduled plans; noun の or dictionary form
volitional form|Plain proposal and intention stem
ようと おもいます|Intention using volitional form
と おもいます|Thought and opinion
と いいます|Naming and quotation
と いって いました|Reported statement
か / かどうか|Embedded questions and whether
んです / のです|Explanatory framing
ので|Reason with explanatory tone
し ... し|Accumulating reasons or qualities
のに|Unexpected contrast; noun/な adjective なのに
ても / でも|Even if; conditional concession
かもしれません|Possibility
はずです|Evidence-based expectation
でしょう / だろう|Probable judgment; register
そうです (hearsay)|Report from a source; plain form
そうです (appearance)|Looks/seems; stem form and exceptions'''),
('N4 changes and preparation',6,'''potential form|Ability; group rules and できる / こられる
ように なります|Change in ability or habit
ことに なります|Externally determined arrangement
ことに します|Personal decision
ように します|Make an effort to maintain a behavior
ように|Purpose with ability/nonvolitional outcome
ために|Purpose with intentional action; noun の
て みます|Try an action experimentally
て おきます|Prepare in advance or leave as is
て しまいます|Completion or unwanted outcome
て あります|Intentional resulting state of a transitive action
transitive/intransitive pairs|Distinguish action on an object from state/change
く / に なります|Adjectival change
く / に します|Make something a particular state
ながら|Same-agent simultaneous actions
はじめます / おわります / つづけます|Start, finish, continue with verb stems
すぎます|Excessive action or quality
やすい / にくい|Ease and difficulty of an action
かた|Way of doing with verb stem
ばかり|Only/mostly; common beginner senses'''),
('N4 conditions and social action',7,'''たら|If/when after a condition is realized
ば / ければ|Conditional verb/adjective forms
なら|Context-based condition or advice
と (conditional)|Regular result; restrictions with requests/intentions
たら どうですか|Suggestion
ほうが いい|Advice with た / ない
なければ / なくては|Obligation patterns and spoken contractions
ては だめ / ちゃ だめ|Prohibition and spoken contraction
あげます / くれます / もらいます|Giving/receiving with perspective
て あげます|Doing a favor; avoid presumptuous use
て くれます|Someone does a favor toward the speaker's side
て もらいます|Receive a favor; agent marked に
て くれませんか|Request a favor
て いただけませんか|Deferential request; bridge register
お ... ください|Polite request with appropriate verb stem
なくて / ないで|Negative cause/linking versus without doing
ずに|Without doing; する becomes せずに
て いきます / て きます|Direction and change relative to now
まだ ... ていません|Not yet; contrast simple negative
ところです|About to / in progress / just finished'''),
('N4 perspective and register',8,'''passive form|Verb formation and affected-person perspective
causative form|Make/let; participant particles
causative-passive recognition|Bridge extension; placement varies
honorific special verbs|いらっしゃる / おっしゃる / なさる / めしあがる
お ... に なります|Productive respectful action pattern
humble special verbs|うかがう / もうす / いたす / まいる / おる
お / ご ... します|Humble pattern with appropriate words
ございます / でございます|Formal existence and copula
ようです|Inference or resemblance; noun の / な adjective な
みたいです|Colloquial resemblance/inference
らしいです|Reported inference or characteristic quality; placement varies
そうに / そうな|Appearance modifying action or noun
さ|Adjectival degree noun
がる / たがる|Observable third-person feelings/desire
か ... か|Alternatives
でも (example)|Suggestion such as tea or something
しか ... ない|Nothing except; negative predicate required
も (quantity)|As many/as much as
も ... も|Both ... and
に する|Choose or decide on an item'''),
('N4 consolidation and bridge',9,'''あいだ / あいだに|Throughout an interval versus event within it
までに|Deadline; contrast まで
ば ... ほど|The more ... the more; bridge placement varies
た ばかり|Recently completed; speaker's perception
ている あいだ|During an ongoing action
ことが あります (occasional)|Sometimes happens; nonpast clause
ことは ... が|Concession recognizing one fact
という|Naming or defining something
かしら / かな|Wondering; register and speaker choice
なさい|Directive with stem; relationship-sensitive
な (prohibition)|Dictionary-form command; recognition first
imperative recognition|Emergency commands; avoid as everyday politeness
て (casual request)|Contextual request with rising intonation
って (quotation/topic)|Conversational compression; explain before reuse
じゃ / ちゃ / とく / てる|Common contractions; map to full forms
sentence-final の / んだ|Explanatory and question intonation
は vs が|Information structure in questions and answers
に vs で|Existence/destination versus action site/means
ている vs てある|Resulting state versus deliberately arranged state
そう vs よう vs らしい|Evidence source and form comparison'''),
('N5 supplementary patterns and variants',3,'''どんな / どうやって|Type-of question and method-of-action question
けど / けれど / けれども|Contrast or an unfinished softening clause
なあ|Reflective or emotional sentence ending
ないと いけない / なくちゃ / なきゃ|Obligation variants; teach the omitted full ending
のが すき / のが じょうず|Nominalized action as preference or skill
のでしょうか|Tentative explanatory question; formal bridge
だれか / なにか / どこか|Indefinite person, thing and place
だれも / なにも / どこにも + negative|No one, nothing and nowhere with appropriate particles
ましょう vs よう|Polite and plain proposal contrast
に / と あいます|Meeting a person; particle perspective'''),
('N4 supplementary constructions',6,'''まま|An existing condition is maintained
ばあいは|Set up a circumstance for an instruction or outcome
だけで|A limited action or means is sufficient
だします|Stem compound for a sudden start
が ひつよう / ひつようが あります|Needed thing versus necessary action
が します|Sensory impression with sound, smell or taste nouns
がり|Person characterized by sensitivity or a tendency
はずが ありません|Strong expectation that something cannot be so
から / で つくります|Source material versus material/means
ころ / ごろ|Approximate period or time; distinguish quantity ぐらい
おきに|Repeated interval; make the intended interval explicit
なかなか ... ない|Expected action remains difficult or unrealized
に きが つきます|Notice a fact or change
に みえます|Appear a certain way to an observer
のに (purpose/use)|Nominalized action + に for utility or required resources
のは ... です|Focus an action or fact as the topic
させて ください|Ask permission to perform an action
たら いいですか|Ask what action would be appropriate
て ほしい|Want another person to do something
て すみません|Apologize for a completed action or situation
て よかった|Express relief about what happened
て やります|Familiar/downward favor expression; relationship-sensitive
て いました|Past ongoing action or past resulting state
て / で (cause)|Link a cause to a nonvolitional result
と ききました / と いわれています|Report what was heard or is commonly said
という こと|Package a quoted proposition as a noun-like unit
と いっても いい|Present a characterization as reasonable
とか ... とか|Offer non-exhaustive examples in conversation
ような / ように|Resemblance modifying a noun or an action
みたいな / みたいに|Conversational noun/action resemblance forms
づらい|Action feels difficult or burdensome
ではないか / じゃないか|Context-sensitive assertion, discovery or appeal for agreement
かい|Familiar yes/no question ending; recognize social tone
ようと します|Attempt or be on the point of an action; bridge placement varies'''),
('N4 discourse and adverbial expressions',7,'''または|Written or formal choice between alternatives
それでも|Continue despite the previous fact
それに|Add another supporting consideration
きっと|Strong confidence, without turning a guess into a fact
きゅうに|An abrupt change or onset
さっき|A recent moment before now
さすが|A result matches an established reputation or expectation
そんなに|Degree referring back to context
やっと|Completion after waiting or effort
ぜひ|An emphatic invitation, recommendation or wish'''),
('N5 conversational building blocks',2,'''を ください|Request an item; contrast action request てください
お / ご|Conventional respectful or beautifying prefixes; not freely added to every word
しかし|A more formal contrast between statements
それから / そして|Sequence or addition across sentences
とても|High degree; combine with appropriate predicates
は どうですか|Ask for an assessment or suggest an option''')]

def inventory():
    out=[]
    for group,ch,rows in GROUPS:
        for row in rows.splitlines():
            p,e=row.split('|',1)
            out.append(dict(id=f'G{len(out)+1:03}',group=group,chapter=ch,pattern=p,explanation=e,status='planned'))
    return out

if __name__=='__main__':
    (ROOT/'master_prompt.txt').write_text(PROMPT,encoding='utf-8')
    (ROOT/'grammar_inventory.json').write_text(json.dumps(inventory(),ensure_ascii=False,indent=2),encoding='utf-8')
    print('Saved master prompt and',len(inventory()),'grammar teaching units')
