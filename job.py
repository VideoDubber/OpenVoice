import os
import torch
import traceback
import html
from openvoice import se_extractor
from openvoice.api import ToneColorConverter
from melo.api import TTS
from fastapi import FastAPI, UploadFile, File, Form
from pydantic import BaseModel
from typing import List
from google.cloud import texttospeech
import shutil
import os
import sys
import uuid
import json
import subprocess
from time import sleep
import os
import azure.cognitiveservices.speech as speechsdk
import pandas as pd
# Set the SPEECH_KEY and SPEECH_REGION environment variables
speech_key = "8c6d73094d244e5b9acb206bd4b2183e"
service_region = "eastus"
texts_={ "af": "Vrugte is vol gesonde voedingstowwe soos vitamiene, minerale en vesel. Appels, lemoene, en piesangs bied belangrike voedingstowwe wat die immuunstelsel versterk en die liggaam help om infeksies te beveg. Vrugte bevat antioksidante wat die risiko van chroniese siektes soos hartsiektes en kanker kan verminder. Die natuurlike suikers in vrugte gee jou energie sonder die bykomende kalorieë van verfynde suiker. Vesel in vrugte bevorder 'n gesonde spysverteringstelsel. Gereelde inname van vrugte kan help om die bloeddruk te reguleer, cholesterolvlakke te verlaag en gesonde vel en hare te ondersteun.",
  "sq": "Frutat janë të mbushura me lëndë ushqyese të shëndetshme si vitamina, minerale dhe fibra. Mollët, portokallet dhe bananet ofrojnë lëndë ushqyese të rëndësishme që forcojnë sistemin imunitar dhe ndihmojnë trupin të luftojë infeksionet. Frutat përmbajnë antioksidantë që mund të ulin rrezikun e sëmundjeve kronike si sëmundjet e zemrës dhe kanceri. Sheqernat natyrale në fruta ju japin energji pa kaloritë shtesë të sheqerit të rafinuar. Fibrat në fruta promovojnë një sistem të shëndetshëm të tretjes. Marrja e rregullt e frutave mund të ndihmojë në rregullimin e presionit të gjakut, uljen e niveleve të kolesterolit dhe mbështetjen e lëkurës dhe flokëve të shëndetshëm.",
  "am": "ፍሬዎች እንደ ቪታሚኖች፣ ማዕድናቶችና እንጨት ያሉ ጤናማ ምግብ ነበርተኞች እንዲሁም በቀላሉ ምግባቸውን እንዲያበሉ የሚያደርጋቸው ምግብ ነው። አፖሎች፣ ብርቱካናት እና ማንጎዎች እንደ ጤናማ ስርዓት ተረጎሙበት እና ምንጮች በከፍተኛ ደረጃ እንደሚለው በቀላሉ እንዲያስቀላቀሉ የሚያደርጋቸው ነው። ፍሬዎች ሕመምን እና በሽታዎችን በቀላሉ እንዲያስቀላቀሉ የሚያደርጋቸውን አንግልሽኖች ያካተቱ ናቸው። ምግቡን እንዲያበሉ የሚያደርጋቸው እንጨት እና ቪታሚኖች እና በቀላሉ እንዲያድርጉ የሚያደርጋቸው እንደሚያደርጋቸው ነው።",
  "ar": "تحتوي الفواكه على مجموعة متنوعة من الفيتامينات والمعادن والألياف الضرورية لصحة الجسم. الفواكه مثل التفاح والبرتقال والموز تحتوي على عناصر غذائية هامة تعزز مناعة الجسم وتساعده على مكافحة الأمراض. تحتوي الفواكه على مضادات أكسدة قد تساعد في تقليل خطر الإصابة بالأمراض المزمنة مثل أمراض القلب والسرطان. السكر الطبيعي في الفواكه يمنح الجسم الطاقة دون السعرات الحرارية الزائدة من السكر المكرر. الألياف الموجودة في الفواكه تساعد في تحسين عملية الهضم. تناول الفواكه بانتظام يمكن أن يساعد في تنظيم ضغط الدم، خفض مستويات الكوليسترول، ودعم صحة الجلد والشعر.",
  "hy": "Մրգերը պարունակում են բազմաթիվ օգտակար սննդանյութեր, ինչպիսիք են վիտամինները, հանքանյութերը և մանրաթելերը։ Խնձորները, նարինջները և բանանները ապահովում են կարևոր սննդանյութեր, որոնք ուժեղացնում են իմունային համակարգը և օգնում են մարմնին պայքարել վարակների դեմ։ Մրգերը պարունակում են հակաօքսիդանտներ, որոնք կարող են նվազեցնել սրտային հիվանդությունների և քաղցկեղի ռիսկը։ Մրգերի մեջ բնական շաքարները տալիս են էներգիա առանց հավելյալ կալորիաների։ Մրգերում առկա մանրաթելերը նպաստում են առողջ մարսողական համակարգին։ Մրգերի կանոնավոր ընդունումը կարող է օգնել կարգավորել արյան ճնշումը, նվազեցնել խոլեստերինի մակարդակը և աջակցել առողջ մաշկին ու մազերին։",
  "as": "ফলবোৰত বহুল পৰিমাণে স্বাস্থ্যকৰ পুষ্টি, যেনে ভিটামিন, খনিজ আৰু পিষ্ট আছে। আপেল, কমলা আৰু কলবোৰত গুৰুত্বপূর্ণ পুষ্টি থাকে, যিবোৰে ৰোগ-প্ৰতিৰোধ ক্ষমতা বঢ়ায় আৰু শৰীৰক সংক্ৰমণৰ বিৰুদ্ধে লড়াই কৰিবলৈ সহায় কৰে। ফলবোৰত অ্যান্টিঅক্সিডেণ্ট থাকে, যিসকলে হৃদৰোগ আৰু কেঞ্চাৰ যেনে দীঘলীয়া ৰোগৰ বিপদ হ্ৰাস কৰিব পাৰে। ফলত থকা প্ৰাকৃতিক চেনিয়ে আপোনাক অধিক কেল'ৰি নোহোৱাকৈ শক্তি যোগায়। ফলৰ পিষ্টে সুস্থ পৰিপাক প্ৰণালীক সহায় কৰে। নিয়মীয়াকৈ ফল খাবলেৰে ৰক্তচাপ নিয়ন্ত্ৰণ, ক'লেষ্টেৰ'লৰ পৰিমাণ হ্ৰাস আৰু সুস্থ ত্বক আৰু চুলিৰ স্বাস্থ্যৰ পৰা লাভ কৰিব পাৰে।",
  "az": "Meyvələr vitaminlər, minerallar və liflərlə zəngindir. Almalar, portağallar və bananlar immun sistemini gücləndirən və orqanizmi infeksiyalardan qoruyan vacib qidalar təmin edir. Meyvələrdəki antioksidantlar xroniki xəstəliklər, ürək-damar xəstəlikləri və xərçəng riskini azalda bilər. Meyvələrin tərkibindəki təbii şəkərlər enerji verir, lakin əlavə kalori təmin etmir. Meyvələrdə olan liflər sağlam həzm sistemini dəstəkləyir. Meyvələrin müntəzəm qəbulu qan təzyiqini tənzimləyə, xolesterin səviyyəsini aşağı sala və sağlam dəri və saçların saxlanmasına kömək edə bilər.",
  "bn": "ফলগুলিতে প্রচুর পুষ্টি যেমন ভিটামিন, খনিজ এবং ফাইবার রয়েছে। আপেল, কমলা, এবং কলার মতো ফলগুলি গুরুত্বপূর্ণ পুষ্টি সরবরাহ করে যা রোগ প্রতিরোধ ক্ষমতা বাড়ায় এবং দেহকে সংক্রমণের বিরুদ্ধে লড়াই করতে সহায়তা করে। ফলগুলি অ্যান্টিঅক্সিডেন্ট সমৃদ্ধ, যা হৃদরোগ এবং ক্যান্সারের মতো দীর্ঘমেয়াদী রোগের ঝুঁকি কমাতে পারে। ফলের প্রাকৃতিক চিনি আপনাকে অতিরিক্ত ক্যালোরি ছাড়াই শক্তি দেয়। ফলের ফাইবার সুস্থ পাচনতন্ত্রকে সহায়তা করে। নিয়মিত ফল খাওয়া রক্তচাপ নিয়ন্ত্রণ করতে, কোলেস্টেরলের মাত্রা কমাতে এবং সুস্থ ত্বক এবং চুলকে সমর্থন করতে পারে।",
  "eu": "Frutak bitamina, mineral eta zuntz osasuntsuekin beteta daude. Sagarrek, laranjek eta platanoek elikagai garrantzitsuak eskaintzen dituzte, immunitate-sistema indartzen dutenak eta gorputzak infekzioei aurre egiten laguntzen diotenak. Frutak antioxidatzaileak dituzte, gaixotasun kronikoen, bihotzeko gaixotasunen eta minbiziaren arriskua murrizten lagun dezaketenak. Frutetan dagoen azukre naturalak energia ematen dizu kaloria gehigarririk gabe. Frutak dituen zuntzak digestio-sistema osasuntsu bat sustatzen du. Fruta erregularrak odol-presioa erregulatzen, kolesterol-mailak jaisten eta azala eta ilea osasuntsuak laguntzen ditu.",
  "bs": "Voće je bogato vitaminima, mineralima i vlaknima koja su ključna za zdravlje. Jabuke, narandže i banane pružaju važne hranljive materije koje jačaju imunološki sistem i pomažu tijelu da se bori protiv infekcija. Voće sadrži antioksidante koji mogu smanjiti rizik od hroničnih bolesti kao što su srčane bolesti i rak. Prirodni šećeri u voću pružaju energiju bez dodatnih kalorija iz rafiniranog šećera. Vlakna u voću promovišu zdravu probavu. Redovno konzumiranje voća može pomoći u regulaciji krvnog pritiska, snižavanju nivoa holesterola i održavanju zdrave kože i kose.",
  "bg": "Плодовете са пълни със здравословни хранителни вещества като витамини, минерали и фибри. Ябълките, портокалите и бананите осигуряват важни хранителни вещества, които укрепват имунната система и помагат на организма да се бори с инфекциите. Плодовете съдържат антиоксиданти, които могат да намалят риска от хронични заболявания като сърдечни заболявания и рак. Естествените захари в плодовете ви дават енергия без допълнителни калории от рафинираната захар. Фибрите в плодовете подпомагат здравословната храносмилателна система. Редовната консумация на плодове може да помогне за регулиране на кръвното налягане, намаляване на нивата на холестерола и поддържане на здрава кожа и коса.",
  "my": "သစ်သီးများသည် ကျန်းမာရေးအတွက် အလွန်အကျိုးရှိပါသည်။ သစ်သီးများတွင် ဗီတာမင်များနှင့် ဗျူဟာဓာတ်များ ပါဝင်ပြီး ကိုယ်ခံအားကို မြှင့်တင်ပေးသည်။ ပန်းသီး၊ နာနတ်သီး၊ နှမ်းသီးတို့သည် အာဟာရဓာတ် များစွာပါဝင်ပြီး ခန္ဓာကိုယ်ကို နေလောင်ဒဏ်ကာကွယ်ပေးပါသည်။ သွေးတွင်းဆီးချို၊ နှလုံးရောဂါ ကာကွယ်ပေးသည်။ အရက်စားသုံးမှုနှင့် ဆီးချိုလက္ခဏာများ လျှော့ချပေးပါသည်။ အချိန်တိုင်း သင့်တော်သော သစ်သီးများကို စားသုံးခြင်းဖြင့် ကျန်းမာရေး မြင့်မားစေပါသည်။ သင့်၏နေ့စဉ်အစားအစာများတွင် သစ်သီးများထည့်သွင်းပါက ကျန်းမာရေးအကျိုးများ များပြားစေပါသည်။",

  "ca": "Les fruites són essencials per a una dieta saludable. Estan plenes de vitamines, minerals i antioxidants que ajuden a mantenir el cos fort i resistent a les malalties. Les pomes, les taronges i els plàtans són exemples de fruites riques en fibra i vitamines C i A, que promouen la salut cardíaca i milloren la digestió. A més, consumir fruita diàriament pot reduir el risc de patir malalties cròniques com la diabetis tipus 2 i la hipertensió. Incloure una varietat de fruites fresques en la dieta diària és una manera deliciosa i eficaç de mantenir-se saludable.",

  "yu": "Ko‘p mevalar tanamiz uchun foydalidir. Ular tarkibida ko‘plab vitaminlar va antioksidantlar mavjud bo‘lib, immunitet tizimini mustahkamlaydi. Olma, banan, apelsinlar kabi mevalar yurak salomatligini yaxshilaydi va qondagi shakar miqdorini boshqarishda yordam beradi. Meva iste'moli yurak-qon tomir kasalliklari va saraton xavfini kamaytiradi. Shuningdek, mevalar ovqat hazm qilishni osonlashtiradi va energiya beradi. Har kuni meva iste'mol qilish sog‘lom turmush tarzining muhim qismidir va kasalliklardan saqlanishga yordam beradi. Mevalarni ratsioningizga qo'shish sizning umumiy sog'lig'ingiz uchun foydalidir.",

  "zh": "水果对健康至关重要。它们富含维生素、矿物质和抗氧化剂，有助于增强免疫系统并预防疾病。苹果、橙子和香蕉是富含纤维和维生素C的水果，能够促进心脏健康并改善消化。每天食用水果有助于降低患上慢性疾病如二型糖尿病和高血压的风险。水果的天然糖分也可以提供能量，同时不会对血糖造成巨大波动。为了保持健康，建议将多种水果纳入日常饮食中，享受它们带来的美味和营养益处。",

  "wu": "水果对健康非常重要。水果富含维生素、矿物质和抗氧化剂，帮助增强免疫力和预防疾病。苹果、橙子和香蕉是富含纤维和维生素C的水果，有助于心脏健康和改善消化。每天吃水果可以减少患慢性病如二型糖尿病和高血压的风险。水果的天然糖分提供能量，同时不会引起血糖大幅波动。为了保持健康，建议在日常饮食中加入多种水果，享受它们带来的美味和营养。",

  "hr": "Voće je ključno za zdravu prehranu. Bogato je vitaminima, mineralima i antioksidansima koji pomažu u jačanju imuniteta i sprječavanju bolesti. Jabuke, naranče i banane su primjeri voća bogatog vlaknima i vitaminima C i A, što potiče zdravlje srca i poboljšava probavu. Redovita konzumacija voća može smanjiti rizik od kroničnih bolesti poput dijabetesa tipa 2 i visokog krvnog tlaka. Uključivanje raznovrsnog svježeg voća u dnevnu prehranu izvrstan je način za održavanje zdravlja i vitalnosti.",

  "cs": "Ovoce je nezbytnou součástí zdravé stravy. Obsahuje vitamíny, minerály a antioxidanty, které podporují imunitní systém a chrání před nemocemi. Jablka, pomeranče a banány jsou bohaté na vlákninu a vitamíny C a A, které podporují zdraví srdce a zlepšují trávení. Pravidelná konzumace ovoce může snížit riziko vzniku chronických onemocnění, jako je cukrovka typu 2 a vysoký krevní tlak. Zahrnutí různých druhů ovoce do každodenní stravy je chutný a účinný způsob, jak si udržet zdraví a vitalitu.",

  "da": "Frugt er afgørende for en sund kost. De er fyldt med vitaminer, mineraler og antioxidanter, som hjælper med at styrke immunforsvaret og forebygge sygdomme. Æbler, appelsiner og bananer er eksempler på frugter rige på fibre og vitaminer C og A, som fremmer hjertesundheden og forbedrer fordøjelsen. At spise frugt dagligt kan reducere risikoen for kroniske sygdomme som type 2-diabetes og forhøjet blodtryk. At inkludere en række friske frugter i din daglige kost er en lækker og effektiv måde at holde sig sund på.",

  "nl": "Fruit is essentieel voor een gezond dieet. Ze zitten boordevol vitamines, mineralen en antioxidanten die helpen het immuunsysteem te versterken en ziekten te voorkomen. Appels, sinaasappels en bananen zijn voorbeelden van fruit dat rijk is aan vezels en vitamine C en A, wat de gezondheid van het hart bevordert en de spijsvertering verbetert. Dagelijks fruit eten kan het risico op chronische ziekten zoals diabetes type 2 en hoge bloeddruk verminderen. Het opnemen van een verscheidenheid aan vers fruit in je dagelijkse voeding is een heerlijke en effectieve manier om gezond te blijven.",

  "en": "Fruits are vital for a healthy diet. They are packed with vitamins, minerals, and antioxidants that help boost the immune system and prevent diseases. Apples, oranges, and bananas are examples of fruits rich in fiber and vitamins C and A, which promote heart health and improve digestion. Eating fruits daily can reduce the risk of chronic diseases like type 2 diabetes and high blood pressure. Including a variety of fresh fruits in your daily diet is a delicious and effective way to maintain health and vitality.",

  "et": "Puuviljad on tervisliku toitumise oluline osa. Need sisaldavad rohkesti vitamiine, mineraalaineid ja antioksüdante, mis aitavad tugevdada immuunsüsteemi ja ennetada haigusi. Õunad, apelsinid ja banaanid on näiteks puuviljad, mis on rikkad kiudainete ning vitamiinide C ja A poolest, mis soodustavad südame tervist ja parandavad seedimist. Igapäevane puuviljade tarbimine võib vähendada krooniliste haiguste, nagu 2. tüüpi diabeet ja kõrge vererõhk, riski. Erinevate värskete puuviljade lisamine igapäevasesse toidulauale on maitsev ja tõhus viis tervise säilitamiseks.",
  
    "fi": "Hedelmät, kuten omenat, appelsiinit ja banaanit, ovat täynnä vitamiineja ja mineraaleja, jotka tukevat terveyttä. Esimerkiksi C-vitamiini vahvistaa immuunijärjestelmää ja auttaa torjumaan infektioita. Kuidut pitävät ruoansulatuksen kunnossa ja voivat auttaa alentamaan kolesterolia. Antioksidantit suojaavat soluja vaurioilta ja voivat vähentää kroonisten sairauksien riskiä. Hedelmät ovat myös luonnollinen energianlähde ja voivat auttaa pitämään verenpaineen normaalina. Monipuolinen hedelmien nauttiminen päivittäin voi parantaa yleistä hyvinvointia ja edistää pitkäikäisyyttä.",
    
    "fr": "Les fruits comme les pommes, les oranges et les bananes sont riches en vitamines et minéraux essentiels à la santé. La vitamine C, par exemple, renforce le système immunitaire et aide à lutter contre les infections. Les fibres favorisent une bonne digestion et peuvent aider à réduire le cholestérol. Les antioxydants protègent les cellules des dommages et peuvent réduire le risque de maladies chroniques. Les fruits sont également une source naturelle d'énergie et peuvent aider à maintenir une pression artérielle normale. Consommer une variété de fruits quotidiennement peut améliorer le bien-être général et favoriser la longévité.",
  
    "gl": "As froitas como as mazás, as laranxas e os plátanos están cheas de vitaminas e minerais esenciais para a saúde. A vitamina C, por exemplo, fortalece o sistema inmunitario e axuda a combater as infeccións. As fibras favorecen unha boa dixestión e poden axudar a reducir o colesterol. Os antioxidantes protexen as células dos danos e poden reducir o risco de enfermidades crónicas. As froitas tamén son unha fonte natural de enerxía e poden axudar a manter unha presión arterial normal. Consumir unha variedade de froitas diariamente pode mellorar o benestar xeral e favorecer a lonxevidade.",
  
    "ka": "ხილი, როგორიცაა ვაშლი, ფორთოხალი და ბანანი, სავსეა ვიტამინებითა და მინერალებით, რომლებიც მნიშვნელოვანია ჯანმრთელობისთვის. C ვიტამინი აძლიერებს იმუნურ სისტემას და ეხმარება ინფექციებთან ბრძოლას. ბოჭკოვანი ხელს უწყობს საჭმლის მომნელებელ პროცესს და ხელს უწყობს ქოლესტერინის დონის დაწევას. ანტიოქსიდანტები იცავს უჯრედებს დაზიანებისგან და ამცირებს ქრონიკული დაავადებების რისკს. ხილი ასევე არის ენერგიის ბუნებრივი წყარო და ეხმარება სისხლის წნევის ნორმალიზაციას. ყოველდღიურად მრავალფეროვანი ხილის მიღება ხელს უწყობს საერთო კეთილდღეობას და ხანგრძლივობას.",
  
    "de": "Früchte wie Äpfel, Orangen und Bananen sind reich an Vitaminen und Mineralstoffen, die für die Gesundheit wichtig sind. Vitamin C stärkt das Immunsystem und hilft, Infektionen abzuwehren. Ballaststoffe fördern eine gesunde Verdauung und können helfen, den Cholesterinspiegel zu senken. Antioxidantien schützen die Zellen vor Schäden und können das Risiko chronischer Erkrankungen verringern. Früchte sind auch eine natürliche Energiequelle und können helfen, den Blutdruck im Normalbereich zu halten. Der tägliche Verzehr einer Vielzahl von Früchten kann das allgemeine Wohlbefinden verbessern und die Lebensdauer fördern.",
  
    "el": "Τα φρούτα όπως τα μήλα, τα πορτοκάλια και οι μπανάνες είναι πλούσια σε βιταμίνες και ανόργανα συστατικά που είναι σημαντικά για την υγεία. Η βιταμίνη C ενισχύει το ανοσοποιητικό σύστημα και βοηθά στην καταπολέμηση των λοιμώξεων. Οι φυτικές ίνες προάγουν την υγιή πέψη και μπορούν να βοηθήσουν στη μείωση της χοληστερόλης. Τα αντιοξειδωτικά προστατεύουν τα κύτταρα από βλάβες και μπορούν να μειώσουν τον κίνδυνο χρόνιων ασθενειών. Τα φρούτα είναι επίσης μια φυσική πηγή ενέργειας και μπορούν να βοηθήσουν στη διατήρηση φυσιολογικής αρτηριακής πίεσης. Η καθημερινή κατανάλωση ποικιλίας φρούτων μπορεί να βελτιώσει τη γενική ευεξία και να προάγει τη μακροζωία.",
  
    "gu": "ફળો જેમ કે સફરજન, નારંગી અને કેલા વિટામિન અને ખનિજોથી ભરપૂર હોય છે જે આરોગ્ય માટે જરૂરી છે. વિટામિન C, ઉદાહરણ તરીકે, રોગપ્રતિકારક શક્તિમાં વધારો કરે છે અને ચેપ સામે લડવામાં મદદ કરે છે. ફાઇબર સારી પાચન ક્રિયાને પ્રોત્સાહન આપે છે અને કોલેસ્ટ્રોલ ઘટાડવામાં મદદરૂપ બને છે. એન્ટીઓક્સિડન્ટ્સ કોષોને નુકસાનથી બચાવે છે અને ક્રોનિક બીમારીઓના જોખમને ઘટાડે છે. ફળો એ ઉર્જાનો પ્રાકૃતિક સ્ત્રોત પણ છે અને તે નોર્મલ બ્લડ પ્રેશર જાળવવામાં મદદ કરે છે. રોજે વિવિધ પ્રકારના ફળોનું સેવન સામાન્ય કલ્યાણમાં સુધારો કરી શકે છે અને દીર્ઘાયુષ્યને પ્રોત્સાહિત કરી શકે છે.",
  
    "he": "פירות כמו תפוחים, תפוזים ובננות מלאים בויטמינים ומינרלים החשובים לבריאות. ויטמין C, למשל, מחזק את מערכת החיסון ועוזר להילחם בזיהומים. הסיבים התזונתיים תורמים לעיכול תקין ועשויים לסייע בהורדת רמת הכולסטרול. נוגדי חמצון מגנים על התאים מנזקים ועשויים להקטין את הסיכון למחלות כרוניות. פירות הם גם מקור טבעי לאנרגיה ועשויים לסייע בשמירה על לחץ דם תקין. צריכת מגוון פירות על בסיס יומי יכולה לשפר את הבריאות הכללית ולתרום לאריכות ימים.",
  
    "hi": "फल जैसे सेब, संतरा और केला विटामिन और खनिजों से भरपूर होते हैं जो स्वास्थ्य के लिए महत्वपूर्ण हैं। उदाहरण के लिए, विटामिन सी प्रतिरक्षा प्रणाली को मजबूत करता है और संक्रमण से लड़ने में मदद करता है। फाइबर अच्छी पाचन क्रिया को बढ़ावा देता है और कोलेस्ट्रॉल को कम करने में मदद कर सकता है। एंटीऑक्सिडेंट कोशिकाओं को नुकसान से बचाते हैं और पुरानी बीमारियों के जोखिम को कम कर सकते हैं। फल प्राकृतिक ऊर्जा का स्रोत भी हैं और रक्तचाप को सामान्य बनाए रखने में मदद कर सकते हैं। रोजाना विभिन्न फलों का सेवन सामान्य कल्याण में सुधार कर सकता है और दीर्घायु को बढ़ावा दे सकता है।",
  
    "hu": "A gyümölcsök, mint például az alma, a narancs és a banán, tele vannak vitaminokkal és ásványi anyagokkal, amelyek elengedhetetlenek az egészséghez. A C-vitamin például erősíti az immunrendszert, és segít a fertőzések leküzdésében. A rostok elősegítik az emésztést és segíthetnek a koleszterinszint csökkentésében. Az antioxidánsok védik a sejteket a károsodástól, és csökkenthetik a krónikus betegségek kockázatát. A gyümölcsök természetes energiaforrást is jelentenek, és segíthetnek a normális vérnyomás fenntartásában. A napi gyümölcsfogyasztás javíthatja az általános jólétet és elősegítheti a hosszú életet.",
  
    "is": "Ávextir eins og epli, appelsínur og bananar eru fullir af vítamínum og steinefnum sem eru mikilvæg fyrir heilsuna. C-vítamín styrkir ónæmiskerfið og hjálpar til við að berjast gegn sýkingum. Trefjar stuðla að góðri meltingu og geta hjálpað til við að lækka kólesteról. Andoxunarefni vernda frumur gegn skemmdum og geta dregið úr hættu á langvinnum sjúkdómum. Ávextir eru líka náttúruleg orkuuppspretta og geta hjálpað til við að viðhalda eðlilegu blóðþrýstingi. Að borða fjölbreytt úrval af ávöxtum daglega getur bætt almenna vellíðan og stuðlað að langlífi.",
    "id": "Buah-buahan seperti apel, pisang, dan jeruk kaya akan vitamin dan mineral yang penting untuk kesehatan. Mereka membantu menjaga berat badan, meningkatkan pencernaan, dan mendukung sistem kekebalan tubuh. Buah-buahan juga mengandung antioksidan yang melindungi tubuh dari kerusakan akibat radikal bebas.",
  "iu": "ᐃᓐᓂᐊᑉ ᓂᕈᐊᒃᓴᐃᑦ ᓂᕐᒥᐊᕐᕕᑦ ᐊᑭᓐᓂᐊᑉ ᐊᑭᓐᓂᕈᒪᓚᐃᑦ ᓇᓂᕐᓂᐊᑉ ᑭᓐᓂᕐᒥᐊᕐᕕᑦ. ᐃᓐᓂᐊᑉ ᓂᕈᐊᒃᓴᐃᑦ ᐊᑭᓐᓂᕈᒪᓚᐃᑦ ᐊᑭᓐᓂᕐᒥᐊᕐᕕᑦ ᓇᓂᕐᓂᐊᑉ ᑭᓐᓂᕐᒥᐊᕐᕕᑦ ᐊᑭᓐᓂᕐᒥᐊᕐᕕᑦ.",
  "ga": "Tá toraidh cosúil le úlla, banana agus oráiste chomh maith le vitimíní agus mianraí a chuidítear le sláinte. Cabhraíonn siad cothromaíocht meáchain a choinneáil, an diúchas a fheabhsú agus tacaíocht don chóras imdhíonachta. Tá frith-ocsaideoirí chomh maith i dtoraí a chosnaíonn an cholainn ó damáiste a tharlaíonn mar gheall ar radacail shaora.",
  "it": "La frutta come mele, banane e arance sono ricche di vitamine e minerali importanti per la salute. Aiutano a mantenere il peso, migliorare la digestione e supportare il sistema immunitario. La frutta contiene anche antiossidanti che proteggono il corpo dal danno causato dai radicali liberi.",
  "ja": "リンゴ、バナナ、オレンジなどの果物は、ビタミンやミネラルが豊富で、健康に役立ちます。これらは、体重を管理し、消化を改善し、免疫システムをサポートします。果物には、抗酸化物質も含まれており、体を自由基の損傷から守ります。",
  "jv": "Woh-wohan kayadene apel, pisang, lan jeruk kaya akan vitamin lan mineral sing penting kanggo kaséhatan. Dheweke mbiyantu njaga abot, nambahake pencernaan, lan ndukung sistem kekebalan awak. Woh-wohan uga ngandhut antioksidan sing njaga awak saka kerusakan amarga radikal bebas.",
  
    "kn": "ಹಣ್ಣುಗಳು ಆಪಿಲ್, ಬಾಳೆಹಣ್ಣು ಮತ್ತು ಕಿತ್ತಳೆ ವಿಟಮಿನ್‌ಗಳು ಮತ್ತು ಖನಿಜಗಳಿಂದ ಸಮೃದ್ಧವಾಗಿವೆ. ಅವು ತೂಕ ನಿರ್ವಹಿಸಲು, ಜೀರ್ಣಕ್ರಿಯೆಯನ್ನು ಸುಧಾರಿಸಲು ಮತ್ತು ರೋಗನಿರೋಧಕ ವ್ಯವಸ್ಥೆಯನ್ನು ಬೆಂಬಲಿಸಲು ಸಹಾಯ ಮಾಡುತ್ತವೆ. ಹಣ್ಣುಗಳು ಫ್ರೀ ರ್ಯಾಡಿಕಲ್‌ಗಳಿಂದ ದೇಹವನ್ನು ರಕ್ಷಿಸುವ ಆಂಟಿಆಕ್ಸಿಡೆಂಟ್‌ಗಳನ್ನು ಸಹ ಹೊಂದಿವೆ.",
    "kk": "Жемістер алма, банан және апельсин витаминдер мен минералдарға бай. Олар салмақты ұстап, асқазан жұмысын жақсартып, иммунитет жүйесін қолдайды. Жемістер тегін радикалдардан денені қорғайтын антиоксиданттарды да иемденеді.",
    "km": "ផ្លែឈើដូចជា ប្រហុក ចេត្រា និង ស្ពែរ មានវីតាមីន និង ប្រេក្លាបស់ជាច្រើន។ ពួកវាជួយទប់ស្ទះ កាត់បន្ថយការស៊ី និង គាំទ្រប្រព័ន្ធជាតិ។ ផ្លែឈើក៏មាន អង់ទីអុក្សីដង់ ដែលការពាររាងកាយពីការខូចខាតរបស់រ៉ាឌីកាល់ផ្ទាល់ប៉ុណ្ណោះ។",
    
        "sw": "Matunda kama machungwa, maparachichi, na mananasi ni muhimu kwa afya. Yanasaidia kudumisha uzito, kuboresha utumbo, na kusaidia mfumo wa kinga. Matunda pia yana antiosidanti ambazo husaidia kuzuia uharibifu wa seli za mwili.",
        "ko": "과일은 건강에 매우 중요합니다. 사과, 바나나, 오렌지와 같은 과일은 비타민과 미네랄이 풍부하여 체중 관리, 소화 개선, 면역 체계 지원에 도움이 됩니다. 과일에는 또한 자유 라디칼로 인한 손상을 방지하는 항산화제가 포함되어 있습니다.",

            "lo": "ພພລະດູນີ້ ເຊັ່ນ ເມັດ ມະນາວ ແລະ ສົ້ມສານ ແມ່ນສານສຸກ ທີ່ມີປະໂຫຍດສຸກສາລະບາດສຸກກັບສະໝອດຂອງຮຸ່ນ. ພພລະດູນີ້ ສາມາດຊ່ວຍບານຈໍານວນນ່ຳ ແລະ ສະໝອງສຸຂະພາບຂອງຮຸ່ນ.",
            "lv": "Augļi, piemēram, āboli, banāni un apelsīni, ir bagāti ar vitamīniem un minerāliem, kas ir svarīgi veselībai. Tie palīdz saglabāt normālu svaru, uzlabot gremošanu un atbalstīt imūnsistēmu. Augļos ir arī antioksidanti, kas aizsargā ķermeni no brīvo radikāļu kaitējuma.",
            "lt": "Vaisiai, tokiais kaip obuoliai, bananai ir apelsinai, yra turtingi vitamino ir mineralo, kurie yra svarbūs sveikatai. Jie padeda palaikyti normalų svorį, gerinti virškinimą ir remti imuninę sistemą. Vaisiuose taip pat yra antioksidantai, kurie saugo kūną nuo laisvųjų radikalų poveikio.",
            "mk": "Овошјата, како јаболка, банани и портокали, се богати со витамини и минерали кои се важни за здравјето. Тие помагаат во одржувањето на нормална тежина, подобрување на дигестивниот процес и поддршка на имунолошкиот систем. Овошјата содржат и антиоксиданси кои го штитат организмот од оштетување на слободните радикали.",
            "ms": "Buah-buahan seperti epal, pisang dan oren kaya dengan vitamin dan mineral yang penting untuk kesihatan. Mereka membantu mengekalkan berat badan normal, memperbaiki pencernaan dan menyokong sistem imun. Buah-buahan juga mengandungi antioksidan yang melindungi tubuh daripada kerosakan radikal bebas.",
                "ml": "പഴങ്ങൾ ആരോഗ്യത്തിന് വളരെ നല്ലതാണ്. അവ വിറ്റാമിനുകൾ, ധാതുക്കൾ, ആന്റിഓക്‌സിഡന്റുകൾ എന്നിവയാൽ സമൃദ്ധമാണ്. അവ ശരീരത്തിന്റെ രോഗപ്രതിരോധ ശേഷിയെ ശക്തിപ്പെടുത്തുന്നു, വാതക്കെട്ടിനെ പ്രതിരോധിക്കുന്നു, ത്വക്കിന്റെ ആരോഗ്യം പരിപാലിക്കുന്നു.",
                "mt": "Il-frott wieħed għandu benefiċċji għas-saħħa. Jinkludu vitami, minerali, u antiossidanti. Huma jgħinu fit-tonifikazzjoni tas-sistema immunitarja, fl-iżvilupp tas-sistema digerenti, u fil-protezzjoni tal-għajxien.",
                "mr": "फळे आरोग्यासाठी खूप फायदेशीर आहेत. त्यात व्हिटॅमिन्स, मिनरल्स, आणि ॲन्टिऑक्सीडंट्स असतात. ते शरीराची रोगप्रतिकार शक्ती वाढवतात, पाचन प्रक्रिया सुधारतात, आणि त्वचेचे आरोग्य चांगले ठेवतात.",
                "mn": "Шилэнүүд эрүүл мэндэд ихээхэн үлгэрлэг. Витамин, минерал, антивокислодыг агуулна. Эдгээр нь биеийн иммунитетийг бэхжүүлэх, хэрхэлний системийг сайжруулах, арьсны эрүүл мэндийг хадгалахад туслах болно.",
                "ne": "फलहरू स्वास्थ्यको लागि धेरै फाइदाजनक छन्। तिनमा भिटामिन, मिनरल, र एंटिऑक्सिडेन्टहरू हुन्छन्। तिनीहरूले शरीरको रोग प्रतिरोधक क्षमता बढाउन, पाचन प्रणालीलाई सुधार्न, र त्वचाको स्वास्थ्य राख्नमा सहयोग गर्दछन्।",
                "nb": "Frukt er svært sunt. De inneholder vitaminer, mineraler og antioksidanter. De hjelper til å styrke immunforsvaret, forbedre fordøyelsessystemet og beskytte huden.",
                
                    "or": "ଫଳଗୁଡିକ ଯଥା ଆପେଲ୍, ବାନାନା, ଓ ଅନାରସ ଭିଟାମିନ୍ ଓ ଖଣିଜ ପଦାର୍ଥରେ ସମୃଦ୍ଧ। ଏଗୁଡିକ ଶରୀରର ଓଜନ୍ ନିୟନ୍ତ୍ରଣ, ପାଚନ ଶକ୍ତି ବଢାଇବା, ଓ ରୋଗ ପ୍ରତିରୋଧ ଶକ୍ତି ବଢାଇଥାଏ।",
                    "ps": "مېوې لکه تود، کېلې، او نارنج د ويټامينونو او معادنو سرچينه ده. دا مېوې د بدن د وزن د کنټرول، د هضم کولو د ښه کولو، او د روغتیا د ساتلو لپاره ګټور دي.",
                    "fa": "میوه‌هایی مانند سیب، موز و پرتقال سرشار از ویتامین‌ها و مواد معدنی هستند. این میوه‌ها به کنترل وزن بدن، بهبود هضم و تقویت سیستم ایمنی کمک می‌کنند.",
                    "pl": "Owoce takie jak jabłka, banany i pomarańcze są bogate w witaminy i minerały. Pomagają one utrzymać wagę ciała, poprawić trawienie i wspierać system odpornościowy.",
                    "pt": "Frutas como maçãs, bananas e laranjas são ricas em vitaminas e minerais. Elas ajudam a controlar o peso corporal, melhorar a digestão e apoiar o sistema imunológico.",
                    
                        "pa": "ਫਲ ਸਾਡੀ ਸਿਹਤ ਲਈ ਬਹੁਤ ਲਾਭਦਾਇਕ ਹਨ। ਇਹ ਵਿਟਾਮਿਨਾਂ ਅਤੇ ਖਣਿਜਾਂ ਨਾਲ ਭਰਪੂਰ ਹੁੰਦੇ ਹਨ। ਇਹ ਸਾਡੇ ਸ਼ਰੀਰ ਦੀ ਰੋਗ ਪ੍ਰਤੀਰੋਧਕ ਸਮਰੱਥਾ ਨੂੰ ਵਧਾਉਂਦੇ ਹਨ ਅਤੇ ਸਾਡੇ ਪਾਚਨ ਤੰਤਰ ਨੂੰ ਵੀ ਠੀਕ ਰੱਖਦੇ ਹਨ।",
                        "ro": "Fructele sunt foarte benefice pentru sănătatea noastră. Ele sunt pline de vitamine și minerale. Acestea ne întăresc sistemul imunitar și ne ajută să menținem greutatea sănătoasă. Fructele conțin și antioxidanți care ne protejează împotriva stresului oxidativ.",
                        "ru": "Фрукты очень полезны для нашего здоровья. Они богаты витаминами и минералами. Эти вещества укрепляют наш иммунитет и помогают поддерживать здоровый вес. Фрукты также содержат антиоксиданты, которые защищают нас от окислительного стресса.",
                        "sr": "Воће је веома корисно за наше здравље. Богато је витаминима и минералима. Ови састојци јачају наш имунитет и помажу нам да одржавамо здраву тежину. Воће такође садржи антиоксидансе који нас штите од оксидативног стреса.",
                        "si": "පලතුරු අපේ සෞඛ්ය සඳහා මහෝපකාරීයි. ඒවා විටමින් සහ ඛණිජ පදාර්ථයෙන් පිරිපුන්ය. මේවා අපේ රෝග ප්රතිරෝධක පද්ධතිය බලගාන්වයි අපේ පාචන පද්ධතිය ද හොඳින් පවත්වාගෙන යයි.",
                        "sk": "Ovocie je bohaté na vitamíny a minerály, ktoré sú dôležité pre naše zdravie. Napríklad, jablká sú bohaté na vlákninu, ktorá pomáha regulovať trávenie a snižovať hladinu cholesterolu v krvi. Ďalšie ovocie, ako sú banány, sú bohaté na draslík, ktorý pomáha regulovať krvný tlak.",
                            "sl": "Sadje je polno vitaminov in mineralov, ki so pomembni za naše zdravje. Na primer, jabolka so polna vlaknin, ki pomaga uravnavati prebavo in zmanjšati raven Holesterola v krvi. Drugo sadje, kot so banane, so polne kalija, ki pomaga uravnavati krvni tlak.",
                            "so": "Firinjiru waa bayoolojiya ku filan oo loo isticmaalo xarumaha iyo macaamiisha. Tusaale ahaan, tufaaxda waxaa lagu tiriyaa isku-dhafka, oo caawisa inay soo saaraan xarumaha iyo inay sii wadaan heerka kolesterolka ee dhiigga. Firinjirka kale, sida muuska, waxaa lagu tiriyaa kalium, oo caawisa inay soo saaraan xarumaha.",
                            "es": "La fruta es rica en vitaminas y minerales esenciales para nuestra salud. Por ejemplo, las manzanas son ricas en fibra, lo que ayuda a regular el tránsito intestinal y reducir los niveles de colesterol en la sangre. Otras frutas, como los plátanos, son ricas en potasio, lo que ayuda a regular la presión arterial.",
                            "su": "Wohyu mangrupa sumber vitamin jeung mineral anu penting pikeun kaséhatan manusa. Contona, apel ngandung serat anu ngabantu ngatur pencernaan jeung nurunkeun tingkat kolesterol dina getih. Wohyu lianna, kayaning pisang, ngandung kalium anu ngabantu ngatur tekenan getih.",
                            "sv": "Frukt är rik på vitaminer och mineraler som är viktiga för vår hälsa. Till exempel är äpplen rika på fiber, vilket hjälper till att reglera tarmtömningen och sänka kolesterolnivåerna i blodet. Andra frukter, som bananer, är rika på kalium, vilket hjälper till att reglera blodtrycket.",
                            
                                "ta": "பழங்கள் நமது ஆரோக்கியத்திற்கு மிகவும் நல்லது. அவை நமது உடலுக்கு தேவையான பல சத்துக்களை அளிக்கின்றன. பழங்கள் நமது தோல், முடி, கண்கள் ஆகியவற்றின் ஆரோக்கியத்தை பாதுகாக்கின்றன.",
                                "te": "పండ్లు మన ఆరోగ్యానికి చాలా మంచివి. అవి మన శరీరానికి కావలసిన ఎన్నో పోషకాలను అందిస్తాయి. పండ్లు మన చర్మం, జుట్టు, కళ్ళు వంటి వాటి ఆరోగ్యాన్ని కాపాడతాయి.",
                                "th": "ผลไม้เป็นอาหารที่ดีต่อสุขภาพของเรา มันให้สารอาหารที่จำเป็นต่อร่างกายของเรา ผลไม้ช่วยดูแลสุขภาพของผิวหนัง, เส้นผม, ดวงตา และส่วนอื่นๆ ของเรา",
                                "tr": "Meyveler sağlığımız için çok faydalıdır. Vücudumuza gerekli olan birçok besini sağlar. Meyveler cildimizin, saçımızın, gözlerimizin ve diğerlerinin sağlığını korur.",
                                "uk": "Фрукти дуже корисні для нашого здоров'я. Вони надають нашому організму багато корисних речовин. Фрукти допомагають підтримувати здоров'я шкіри, волосся, очей та інших органів.",
                                "ur": "پھل ہمارے صحت کے لیے بہت مفید ہیں. وہ ہماری جسمانی ضروریات کو پورا کرتے ہیں. پھل ہماری جلد، بالوں، آنکھوں اور دیگر حصوں کے صحت کا خیال رکھتے ہیں.",
                                    "uz": "Mevalar va ularning sog'liq uchun foydalari. Mevalar vitamin va minerallar bilan boyitilgan, ular inson organizmi uchun zarurdir. Masalan, olmalarda ko'p miqdorda tol bor, bu ichaklarning ishini yaxshilaydi va qonning ko'rsatkichlarini pasaytiradi. Banan kabi boshqa mevalar kaliy bilan boyitilgan, bu qon bosimini tartibga soladi.",
                                    "vi": "Trái cây và lợi ích sức khỏe của chúng. Trái cây giàu vitamin và khoáng chất, cần thiết cho cơ thể con người. Ví dụ, táo chứa nhiều chất xơ, giúp cải thiện tiêu hóa và giảm chỉ số đường huyết. Chuối và các loại trái cây khác chứa kali, giúp điều chỉnh huyết áp.",
                                    "cy": "Ffrwythau a'u buddion iechyd. Mae ffrwythau yn gyfoethog mewn fitamin a minerale, sy'n hanfodol i'r corff dynol. Er enghraifft, mae afalau yn cynnwys llawer o ffibr, sy'n helpu i wella treulio'r bwyd a lleihau lefelau siwgr yn y gwaed. Mae ffrwythau eraill, fel baneli, yn cynnwys potasiwm, sy'n helpu i reoli pwysau gwaed.",
                                    "zu": "Izithelo ezithandwayo kanye nezimpendulo zayo ezempilo. Izithelo zinezivitamini nezimanga, ezidingekayo kakhulu kwezempilo zethu. Kwa mfano, amabele anezinkunzi eziningi, ezincedeza ukuthuthukisa ukuthutha kwezinye izinto kanye nokugcina izikhundla zesikanda esidlule. Izithelo ezinokwenzeka njengebhana zinezikhundla zokaliyamu, ezincedeza ukuthuthukisa amandla wesikanda."}
                                    

                              

                          
  


def create_speech_azure(text,outputname,speech_synthesis_voice_name):
    speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)
    speech_config.speech_synthesis_voice_name=speech_synthesis_voice_name
    audio_config = speechsdk.audio.AudioOutputConfig(filename=outputname)
    speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config,audio_config=audio_config)

    # Specify the text to synthesize
    #text = "Waxaan ahay mid cajiib ah"

    # Specify the language and voice to use for the speech synthesis
    #language = "so-SO"  # Somali language code
    #voice = "so-SO-UbaxNeural"  # Replace with the actual Somali voice name

    # Synthesize speech from the text
    result = speech_synthesizer.speak_text_async(text).get()
    #"so-SO-MuuseNeural"

os.environ['TOKENIZERS_PARALLELISM'] = "false"
default_english_text=""
texts_["bn"]='''নতুন দিনের আলোয়, কলাবাগান এলাকার ড. বিনয় বসু, যিনি কলকাতা বিশ্ববিদ্যালয়ের একজন প্রখ্যাত ভাষাবিজ্ঞানী, বাংলা ভাষার বিভিন্ন ধ্বনিভেদ নির্ধারণের জন্য একটি মিশনে বের হলেন। তার সঙ্গে ছিল তার সহকারী, মীনাক্ষী সেনগুপ্ত। তারা কলকাতার বিভিন্ন অঞ্চল ঘুরে দেখলেন, প্রতিটি এলাকার স্বতন্ত্র উচ্চারণ এবং উপভাষার বৈচিত্র্য তুলে ধরতে।

তাদের যাত্রা শুরু হলো উত্তর কলকাতার শ্যামবাজার থেকে, যেখানে তারা বৈষ্ণব সম্প্রদায়ের একজন প্রাচীন ব্যক্তিত্ব, কেশব ভট্টাচার্যের সাথে সাক্ষাৎ করলেন। তিনি তাদের ‘কৃষ্ণ’ এবং ‘রাধা’ শব্দের সূক্ষ্ম ধ্বনিগত পরিবর্তনগুলি সম্পর্কে জানালেন। এরপর তারা গেলেন সল্টলেকের দিকে, যেখানে মৈত্রী চক্রবর্তী, একজন স্কুলশিক্ষিকা, তাদের ছাত্রছাত্রীদের উচ্চারণের প্রভাবের কথা জানালেন, বিশেষত ‘বই’ এবং ‘গান’ শব্দগুলিতে।

পরবর্তীতে তারা গেলেন দক্ষিণ কলকাতার গড়িয়াহাটে, যেখানে তারা জাদবপুর বিশ্ববিদ্যালয়ের একজন বিশিষ্ট অধ্যাপক, ড. সুকান্ত সেনের লেকচার শুনলেন। তিনি গ্রেট ভাওয়েল শিফট সম্পর্কে আলোকপাত করলেন এবং দেখালেন কিভাবে ‘আম’ এবং ‘আকাশ’ শব্দগুলির ধ্বনিগত বিবর্তন সমাজের পরিবর্তনের সঙ্গে মিলেছে।

দমদমের দিকে গিয়ে, তারা অর্ণব বিশ্বাসের সাথে দেখা করলেন, যিনি একজন কবি এবং তার বাচিক উচ্চারণের রোমান্স ফুটিয়ে তোলেন। অর্ণবের ‘নীল’ এবং ‘ব্রীজ’ শব্দগুলির বিশেষ উচ্চারণ তাদের ভাষার সমৃদ্ধ সাংস্কৃতিক বৈচিত্র্যের প্রতিফলন করে।

'''

datadic = {
    'clone_EN-NEWEST': ['EN_NEWEST', 'EN-Newest', 0], #language, speaker_id, speaker_value
    'clone_EN-US': ['EN', 'EN-US', 0],
    'clone_EN-BR': ['EN', 'EN-BR', 1],
    'clone_EN-INDIA': ['EN', 'EN_INDIA', 2],
    'clone_EN-AU': ['EN', 'EN-AU', 3],
    'clone_EN-DEFAULT': ['EN', 'EN-Default', 4],
    'clone_ES': ['ES', 'ES', 0],
    'clone_FR': ['FR', 'FR', 0],
    'clone_ZH': ['ZH', 'ZH', 1],
    'clone_JP': ['JP', 'JP', 0],
    'clone_KR': ['KR', 'KR', 0]
}

ckpt_converter = 'checkpoints_v2/converter'
device = "cuda:0" if torch.cuda.is_available() else "cpu"


tone_color_converter = ToneColorConverter(f'{ckpt_converter}/config.json', device=device)
tone_color_converter.load_ckpt(f'{ckpt_converter}/checkpoint.pth')

#transfer folder, transfer need.txt, from awsapi
#transfer results after done, transfer done.txt, delete local, from awsgpu
#refs are in final_cut/speakerid.mp3 --> uuid/speakerid/ref.mp3
#tests are to be written to speakerid/1.txt 2.txt based on final file name w

# Assuming you have a function `clone_voice` that does the voice cloning
def clone_voice(projectfolder: str) -> list:
    with open(f'{projectfolder}/data.json',"r") as f:
        data = json.load(f) 
    if("speaker_id" not in data):
        return(convert_color(projectfolder))
         
    ref_audio_path=f"{projectfolder}/ref.mp3"
    filename_texts=data["infolist"]

    speaker_id=data["speaker_id"]
    language,speaker_key,speaker_id=datadic[speaker_id]
    speaker_key = speaker_key.lower().replace('_', '-')

    target_se, audio_name = se_extractor.get_se(ref_audio_path, tone_color_converter, vad=False)
    src_path = f'{projectfolder}/tmp.mp3'
    # Speed is adjustable
    speed = 1.0
    model = TTS(language=language, device=device)
    cloned_audio_paths=[]
    
    source_se = torch.load(f'checkpoints_v2/base_speakers/ses/{speaker_key}.pth', map_location=device)
    for i,filename_text in enumerate(filename_texts):
        model.tts_to_file(filename_text["text"], speaker_id, src_path, speed=speed)
        save_path = f'{projectfolder}/{filename_text["filename"]}.mp3'

        # Run the tone color converter
        encode_message = "@VideoDubber.ai"
        tone_color_converter.convert(
            audio_src_path=src_path, 
            src_se=source_se, 
            tgt_se=target_se, 
            output_path=save_path,
            message=encode_message)


def decode_html_and_encode_to_utf8(input_string):
    # Decode HTML entities to their corresponding characters
    decoded_string = html.unescape(input_string)

    # Encode the decoded string to UTF-8
    utf8_string = decoded_string.encode('utf-8')

    return utf8_string.decode('utf-8')


def translate_text_128(texts,target):

    """Translates text into the target language.

    Target must be an ISO 639-1 language code.
    See https://g.co/cloud/translate/v2/translate-reference#supported_languages
    """
    from google.cloud import translate_v2 as translate

    translate_client = translate.Client()

    # Text can also be a sequence of strings, in which case this method
    # will return a sequence of results for each text.
    if(target.split("-")[0] not in ["zh","mni"]):
        target=target.split("-")[0]
    if(target=="yue"):
        target="zh-TW"
    result = translate_client.translate(texts, target_language=target)
    print(result)

    #print("Text: {}".format(result["input"]))
    #print("Translation: {}".format(result["translatedText"]))
    #print("Detected source language: {}".format(result["detectedSourceLanguage"]))

    return([decode_html_and_encode_to_utf8(i["translatedText"]) for i in result])



def convert_color(projectfolder: str) -> list:
    with open(f'{projectfolder}/data.json',"r") as f:
        data = json.load(f)  
    ref_audio_path=f"{projectfolder}/ref.mp3"
    filename_audios=data["infolist"]
    voicecode=filename_audios[0]["filename"].split("#")[1]

    target_se, audio_name = se_extractor.get_se(ref_audio_path, tone_color_converter, vad=False)
    try:
        source_se = torch.load(f'checkpoints_v2/google_base_speakers/models/{voicecode}.pth', map_location=device)
    except:
        try:
            google_speech_client = texttospeech.TextToSpeechClient()
            audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.MP3)
            voice = texttospeech.VoiceSelectionParams(name=voicecode,language_code="-".join(voicecode.split("-")[:2]))

            audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.MP3)
            outpath=f"checkpoints_v2/google_base_speakers/src/{voicecode}.mp3"
            synthesis_input = texttospeech.SynthesisInput(text=texts_[voicecode[:2]])
            response = google_speech_client.synthesize_speech(input=synthesis_input, voice=voice, audio_config=audio_config)
        
            # The response's audio_content is binary.
            with open(outpath, "wb") as out:
                # Write the response to the output file.
                out.write(response.audio_content)
        except:
            create_speech_azure(texts_[voicecode[:2]],f"checkpoints_v2/google_base_speakers/src/{voicecode}.mp3",voicecode)


        

        source_se, audio_name = se_extractor.get_se(f"checkpoints_v2/google_base_speakers/src/{voicecode}.mp3", tone_color_converter, vad=True)
        torch.save(source_se, f"checkpoints_v2/google_base_speakers/models/{voicecode}.pth")
        

    
    
    
    for i,filename_audio in enumerate(filename_audios):
        save_path = f'{projectfolder}/{filename_audio["filename"]}.mp3'
        #source_se, audio_name = se_extractor.get_se(save_path, tone_color_converter, vad=True)

        # Run the tone color converter
        encode_message = "@VideoDubber.ai"
        tone_color_converter.convert(
            audio_src_path=save_path, 
            src_se=source_se, 
            tgt_se=target_se, 
            output_path=save_path,
            message=encode_message)


while(True):
    for i in os.listdir("./projects/"):
        if(os.path.exists(f"./projects/{i}/need.txt")):
            try:
                if(os.path.exists(f"./projects/{i}/pro.txt")!=(sys.argv[1]=="1")):
                    continue;
            except:
                pass
            print(i)
            try:
                for j in os.listdir(f"./projects/{i}"):
                    if os.path.isdir(f"./projects/{i}/{j}"):
                        clone_voice(f"./projects/{i}/{j}")
                
                with open(f"./projects/{i}/location.txt") as f:
                    target_location=f.read()

                os.system(f'rsync -avz -e "ssh -i /home/ubuntu/authkeys/api_aws.pem" ./projects/{i}/ {target_location}')
                os.system(f'rsync -avz -e "ssh -i /home/ubuntu/authkeys/api_aws.pem" done.txt {target_location}')
            except:
                with open(f"errors.txt","a") as f:
                    traceback.print_exc(file=f) 
                with open(f"{sys.argv[1]}/failed.txt","w") as f:
                    traceback.print_exc(file=f) 
                try:
                    with open(f"./projects/{i}/location.txt") as f:
                        target_location=f.read()
                    os.system(f'rsync -avz -e "ssh -i /home/ubuntu/authkeys/api_aws.pem" {sys.argv[1]}/failed.txt {target_location}')
                except:
                    pass;
                
            cmd=f"rm -rf ./projects/{i}"
            subprocess.run(cmd, shell=True, check=True)
            
    sleep(0.5)

