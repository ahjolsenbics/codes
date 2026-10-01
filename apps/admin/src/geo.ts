import { locale } from './i18n'

type Triple = { zh: string; en: string; ru: string }

function pick(row: Triple | undefined, fallback: string): string {
  locale.value
  if (!row) return fallback
  if (locale.value === 'en-US') return row.en
  if (locale.value === 'ru-RU') return row.ru
  return row.zh
}

function indexRow(map: Record<string, Triple>, row: Triple) {
  map[row.zh] = row
  map[row.en] = row
  map[row.ru] = row
  map[row.en.toLowerCase()] = row
  map[row.ru.toLowerCase()] = row
}

function lookup(map: Record<string, Triple>, raw: unknown): Triple | undefined {
  const s = String(raw || '').trim()
  if (!s) return undefined
  return map[s] || map[s.toLowerCase()]
}

const PLACES: Record<string, Triple> = {
  乌鲁木齐: { zh: '乌鲁木齐', en: 'Urumqi', ru: 'Урумчи' },
  霍尔果斯: { zh: '霍尔果斯', en: 'Khorgos', ru: 'Хоргос' },
  喀什: { zh: '喀什', en: 'Kashgar', ru: 'Кашгар' },
  阿拉山口: { zh: '阿拉山口', en: 'Alashankou', ru: 'Алашанькоу' },
  奎屯: { zh: '奎屯', en: 'Kuitun', ru: 'Куйтүн' },
  库尔勒: { zh: '库尔勒', en: 'Korla', ru: 'Корла' },
  昌吉: { zh: '昌吉', en: 'Changji', ru: 'Чанцзи' },
  石河子: { zh: '石河子', en: 'Shihezi', ru: 'Шихэцзы' },
  哈密: { zh: '哈密', en: 'Hami', ru: 'Хами' },
  伊宁: { zh: '伊宁', en: 'Yining', ru: 'Инин' },
  阿克苏: { zh: '阿克苏', en: 'Aksu', ru: 'Аксу' },
  阿拉木图: { zh: '阿拉木图', en: 'Almaty', ru: 'Алматы' },
  塔什干: { zh: '塔什干', en: 'Tashkent', ru: 'Ташкент' },
  奥什: { zh: '奥什', en: 'Osh', ru: 'Ош' },
  比什凯克: { zh: '比什凯克', en: 'Bishkek', ru: 'Бишкек' },
  阿斯塔纳: { zh: '阿斯塔纳', en: 'Astana', ru: 'Астана' },
  奇姆肯特: { zh: '奇姆肯特', en: 'Shymkent', ru: 'Шымкент' },
  塔拉兹: { zh: '塔拉兹', en: 'Taraz', ru: 'Тараз' },
  新西伯利亚: { zh: '新西伯利亚', en: 'Novosibirsk', ru: 'Новосибирск' },
  莫斯科: { zh: '莫斯科', en: 'Moscow', ru: 'Москва' },
  圣彼得堡: { zh: '圣彼得堡', en: 'St. Petersburg', ru: 'Санкт-Петербург' },
  喀山: { zh: '喀山', en: 'Kazan', ru: 'Казань' },
  叶卡捷琳堡: { zh: '叶卡捷琳堡', en: 'Yekaterinburg', ru: 'Екатеринбург' },
  鄂木斯克: { zh: '鄂木斯克', en: 'Omsk', ru: 'Омск' },
  华沙: { zh: '华沙', en: 'Warsaw', ru: 'Варшава' },
  柏林: { zh: '柏林', en: 'Berlin', ru: 'Берлин' },
  多斯特克: { zh: '多斯特克', en: 'Dostyk', ru: 'Достык' },
  塔尔迪库尔干: { zh: '塔尔迪库尔干', en: 'Taldykorgan', ru: 'Талдыкорган' },
  纳рын: { zh: '纳рын', en: 'Naryn', ru: 'Нарын' },
  安集延: { zh: '安集延', en: 'Andijan', ru: 'Андижан' },
  卡拉干达: { zh: '卡拉干达', en: 'Karaganda', ru: 'Караганда' },
  阿克托别: { zh: '阿克托别', en: 'Aktobe', ru: 'Актобе' },
  科斯塔奈: { zh: '科斯塔奈', en: 'Kostanay', ru: 'Костанай' },
  巴甫洛达尔: { zh: '巴甫洛达尔', en: 'Pavlodar', ru: 'Павлодар' },
  彼得罗巴甫尔: { zh: '彼得罗巴甫尔', en: 'Petropavl', ru: 'Петропавловск' },
  乌拉尔斯克: { zh: '乌拉尔斯克', en: 'Oral', ru: 'Уральск' },
  阿特劳: { zh: '阿特劳', en: 'Atyrau', ru: 'Атырау' },
  克孜勒奥尔达: { zh: '克孜勒奥尔达', en: 'Kyzylorda', ru: 'Кызылорда' },
  卡普恰盖: { zh: '卡普恰盖', en: 'Kapchagay', ru: 'Капшагай' },
  满洲里: { zh: '满洲里', en: 'Manzhouli', ru: 'Маньчжурия' },
  伊尔克什坦: { zh: '伊尔克什坦', en: 'Irkeshtam', ru: 'Иркештам' },
}

const CARGOS: Record<string, Triple> = {
  机械零件: { zh: '机械零件', en: 'Machinery parts', ru: 'Машинные детали' },
  日用百货: { zh: '日用百货', en: 'General merchandise', ru: 'Промтовары' },
  棉纱: { zh: '棉纱', en: 'Cotton yarn', ru: 'Хлопчатобумажная пряжа' },
  电子产品: { zh: '电子产品', en: 'Electronics', ru: 'Электроника' },
  建材: { zh: '建材', en: 'Building materials', ru: 'Стройматериалы' },
  冷链食品: { zh: '冷链食品', en: 'Reefer food', ru: 'Рефрижераторные продукты' },
  汽车配件: { zh: '汽车配件', en: 'Auto parts', ru: 'Автозапчасти' },
  家具: { zh: '家具', en: 'Furniture', ru: 'Мебель' },
  钢材: { zh: '钢材', en: 'Steel', ru: 'Сталь' },
  水果: { zh: '水果', en: 'Fruit', ru: 'Фрукты' },
  家电: { zh: '家电', en: 'Appliances', ru: 'Бытовая техника' },
  轮胎: { zh: '轮胎', en: 'Tires', ru: 'Шины' },
  纺织品: { zh: '纺织品', en: 'Textiles', ru: 'Текстиль' },
  空车回程: { zh: '空车回程', en: 'Empty return', ru: 'Порожний рейс' },
}

const COMPANIES: Record<string, Triple> = {}
const PEOPLE: Record<string, Triple> = {}
const PHRASES: Record<string, Triple> = {}
const CUSTOMS: Record<string, Triple> = {}
const BRANDS: Record<string, Triple> = {}

function companyRow(zh: string, en: string, ru: string) {
  indexRow(COMPANIES, { zh, en, ru })
}

function person(zh: string, en: string, ru: string) {
  indexRow(PEOPLE, { zh, en, ru })
}

function say(zh: string, en: string, ru: string) {
  indexRow(PHRASES, { zh, en, ru })
}

function customsRow(zh: string, en: string, ru: string) {
  indexRow(CUSTOMS, { zh, en, ru })
}

function brandRow(zh: string, en: string, ru: string) {
  indexRow(BRANDS, { zh, en, ru })
}

/** 公司名音译，禁止把「家居」意译成 furniture / мебель。 */
companyRow('哈密家居', 'Hami Jiaju', 'Хами Цзяцзюй')
companyRow('北屯建材', 'Beitun Jiancai', 'Бэйтунь Цзяньцай')
companyRow('天山机电', 'Tianshan Jidian', 'Тяньшань Цзидянь')
companyRow('疏附商贸', 'Shufu Shangmao', 'Шуфу Шанмао')
companyRow('霍尔果斯综保', 'Khorgos Comprehensive Bonded Zone', 'Хоргос СЭЗ')
companyRow('伊犁冷链', 'Ili Cold Chain', 'Или Колд Чейн')
companyRow('口岸汽配', 'Kouan Qipei', 'Коуань Ципэй')
companyRow('巴州棉纺', 'Bazhou Cotton', 'Бачжоу Мяньфан')
companyRow('阿勒泰车队', 'Altay Fleet', 'Алтай Автопарк')
companyRow('克州跨境', 'Kezhou Cross-border', 'Кызылсу Кроссбордер')
companyRow('绿卡车队', 'Green Card Fleet', 'Гринкард Автопарк')
companyRow('新疆丝路跨境物流有限公司', 'Xinjiang Silk Road Cross-border Logistics Co., Ltd.', 'ООО «Синьцзян Сылу Кроссбордер Лоджистикс»')
companyRow('霍尔果斯通达国际货代', 'Khorgos Tongda International Forwarding', 'Хоргос Тунда Интернешнл')
companyRow('喀什西域进出口有限公司', 'Kashgar Xiyu Import & Export Co., Ltd.', 'ООО «Кашгар Сиюй Импорт-Экспорт»')
companyRow('奎屯北疆公路运输', 'Kuitun Beijiang Road Transport', 'Куйтүн Бэйцзян Транспорт')
companyRow('库尔勒大宗货运中心', 'Korla Bulk Freight Center', 'Корла Балк Фрейт')
companyRow('昌吉棉纺运贸', 'Changji Cotton Transport', 'Чанцзи Мяньфан')
companyRow('石河子农资配送', 'Shihezi Agri Distribution', 'Шихэцзы Агро')
companyRow('哈密对俄专线物流', 'Hami Russia Lane Logistics', 'Хами Раша Лейн')
companyRow('伊宁边境仓配', 'Yining Border Warehouse', 'Инин Бордер')
companyRow('阿克苏果蔬冷链', 'Aksu Produce Cold Chain', 'Аксу Колд Чейн')
companyRow('待审货代工作室', 'Pending Forwarder Studio', 'Экспедитор на проверке')
companyRow('阿拉木图通达货代', 'Almaty Tongda Forwarding', 'Алматы Тунда')
companyRow('新西伯利亚欧亚物流', 'Novosibirsk Eurasia Logistics', 'Новосибирск Евразия Лоджистикс')
companyRow('阿斯塔纳公路运贸', 'Astana Road Trade', 'Астана Роуд Трейд')
companyRow('奇姆肯特仓配', 'Shymkent Warehouse', 'Шымкент Склад')
companyRow('莫斯科东方专线', 'Moscow East Lane', 'Москва Ист Лейн')
companyRow('比什凯克口岸物流', 'Bishkek Border Logistics', 'Бишкек Бордер Лоджистикс')
companyRow('叶卡捷琳堡接货中心', 'Yekaterinburg Receiving Center', 'Екатеринбург Приёмка')
companyRow('阿拉木图果蔬冷链', 'Almaty Produce Cold Chain', 'Алматы Колд Чейн')
companyRow('阿拉木图仓配', 'Almaty Warehouse', 'Алматы Склад')
companyRow('新西伯利亚接货中心', 'Novosibirsk Receiving Center', 'Новосибирск Приёмка')
companyRow('乌鲁木齐天山机电有限公司', 'Urumqi Tianshan Jidian Co., Ltd.', 'ООО «Урумчи Тяньшань Цзидянь»')
companyRow('阿斯塔纳承运', 'Astana Carrier', 'Астана Кэрриер')

person('努尔兰·别科夫', 'Nurlan Bekov', 'Нурлан Беков')
person('叶尔博拉特·努尔拉诺夫', 'Yerbolat Nurlanov', 'Ерболат Нурланов')
person('伊万·索科洛夫', 'Ivan Sokolov', 'Иван Соколов')
person('艾达尔·别科夫', 'Aidar Bekov', 'Айдар Беков')
person('努尔兰·卡西莫夫', 'Nurlan Kassymov', 'Нурлан Касымов')
person('谢尔盖·奥尔洛夫', 'Sergey Orlov', 'Сергей Орлов')
person('达尼亚尔·斯马古洛夫', 'Daniyar Smagulov', 'Данияр Смагулов')
person('阿列克谢·彼得罗夫', 'Alexey Petrov', 'Алексей Петров')
person('吴斌', 'Wu Bin', 'У Бинь')
person('巴克特詹·托列乌奥夫', 'Bakhytzhan Toleuov', 'Бахытжан Толеуов')
person('德米特里·沃尔科夫', 'Dmitry Volkov', 'Дмитрий Волков')
person('努尔兰·阿力', 'Nurlan Ali', 'Нурлан Али')
person('谢尔盖·伊万诺夫', 'Sergei Ivanov', 'Сергей Иванов')
person('王敏', 'Wang Min', 'Ван Минь')
person('赵建军', 'Zhao Jianjun', 'Чжао Цзяньцзюнь')
person('李娜', 'Li Na', 'Ли На')
person('买买提·艾力', 'Maimaiti Ali', 'Мамати Али')
person('王磊', 'Wang Lei', 'Ван Лэй')
person('陈雪', 'Chen Xue', 'Чэнь Сюэ')
person('周明', 'Zhou Ming', 'Чжоу Мин')
person('孙伟', 'Sun Wei', 'Сунь Вэй')
person('马丽', 'Ma Li', 'Ма Ли')
person('刘洋', 'Liu Yang', 'Лю Ян')
person('阿依古丽', 'Aygul', 'Айгуль')
person('阿依古丽·萨德科娃', 'Aygul Sadykova', 'Айгуль Садыкова')
person('张倩', 'Zhang Qian', 'Чжан Цянь')
person('彼得罗娃', 'Petrova', 'Петрова')
person('伊万诺夫', 'Ivanov', 'Иванов')
person('阿克托雷', 'Aktore', 'Акторе')
person('阿地力', 'Adil', 'Адыл')
person('拉希莫夫', 'Rakhimov', 'Рахимов')
person('古丽娜·阿赫梅托娃', 'Gulnara Akhmetova', 'Гульнара Ахметова')
person('安娜·库兹涅佐娃', 'Anna Kuznetsova', 'Анна Кузнецова')
person('阿斯卡尔·叶先诺夫', 'Askar Yessenov', 'Аскар Есенов')
person('马拉特·伊萨耶夫', 'Marat Isayev', 'Марат Исаев')
person('奥莉加·斯米尔诺娃', 'Olga Smirnova', 'Ольга Смирнова')
person('努尔苏丹·卡里莫夫', 'Nursultan Karimov', 'Нурсултан Каримов')
person('叶卡捷琳娜·诺维科娃', 'Ekaterina Novikova', 'Екатерина Новикова')
person('萨乌列·努尔加利耶娃', 'Saule Nurgaliyeva', 'Сауле Нургалиева')
person('帕维尔·莫罗佐夫', 'Pavel Morozov', 'Павел Морозов')
person('阿谢特·茹马巴耶夫', 'Asset Zhumabayev', 'Асет Жумабаев')
person('叶尔兰·萨特巴耶夫', 'Yerlan Satbayev', 'Ерлан Сатбаев')
person('尼基塔·库兹涅佐夫', 'Nikita Kuznetsov', 'Никита Кузнецов')
person('阿尔曼·托克托古洛夫', 'Arman Toktogulov', 'Арман Токтогулов')

function aliasPerson(from: string, to: string) {
  const row = PEOPLE[to]
  if (row) PEOPLE[from] = row
}
aliasPerson('Нұрлан Беков', '努尔兰·别科夫')
aliasPerson('Нурлан Беков', '努尔兰·别科夫')
aliasPerson('Нұрлан Қасымов', '努尔兰·卡西莫夫')
aliasPerson('Нурлан Касымов', '努尔兰·卡西莫夫')
aliasPerson('Ерболат Нурланов', '叶尔博拉特·努尔拉诺夫')
aliasPerson('Данияр Смагулов', '达尼亚尔·斯马古洛夫')
aliasPerson('Бақытжан Төлеуов', '巴克特詹·托列乌奥夫')
aliasPerson('Бактжан Толеуов', '巴克特詹·托列乌奥夫')
aliasPerson('Рахимов', '拉希莫夫')
aliasPerson('Петрова', '彼得罗娃')
aliasPerson('Айгуль', '阿依古丽')

customsRow('霍尔果斯海关', 'Khorgos Customs', 'Таможня Хоргоса')
customsRow('满洲里海关', 'Manzhouli Customs', 'Таможня Маньчжурии')
customsRow('阿拉山口海关', 'Alashankou Customs', 'Таможня Алашанькоу')
customsRow('喀什海关', 'Kashgar Customs', 'Таможня Кашгара')
customsRow('伊尔克什坦海关', 'Irkeshtam Customs', 'Таможня Иркештама')
customsRow('多斯特克海关', 'Dostyk Customs', 'Таможня Достык')
customsRow('乌鲁木齐海关', 'Urumqi Customs', 'Таможня Урумчи')

brandRow('解放 J6P', 'FAW Jiefang J6P', 'FAW Цзефан J6P')
brandRow('东风天龙', 'Dongfeng Tianlong', 'Дунфэн Тяньлун')
brandRow('陕汽德龙 X6000', 'Shaanxi Delong X6000', 'Шэньци Дэлун X6000')
brandRow('HOWO T7H', 'HOWO T7H', 'HOWO T7H')
brandRow('欧曼 EST', 'Foton Auman EST', 'Фотон Ауман EST')
brandRow('一汽解放', 'FAW Jiefang', 'FAW Цзефан')

const PACKING: Record<string, Triple> = {
  pallet: { zh: '托盘', en: 'Pallet', ru: 'Паллеты' },
  bulk: { zh: '散货', en: 'Bulk', ru: 'Навал' },
  carton: { zh: '纸箱', en: 'Carton', ru: 'Коробки' },
  crate: { zh: '木箱', en: 'Crate', ru: 'Ящики' },
}

const CLASSES: Record<string, Triple> = {
  general: { zh: '普货', en: 'General', ru: 'Генеральный' },
  reefer: { zh: '冷链', en: 'Reefer', ru: 'Рефрижератор' },
  equipment: { zh: '机械设备', en: 'Equipment', ru: 'Оборудование' },
}

const REMARKS: Record<string, Triple> = {
  'keep dry': { zh: '防潮', en: 'Keep dry', ru: 'Беречь от влаги' },
  'no stack': { zh: '禁止堆叠', en: 'Do not stack', ru: 'Не штабелировать' },
  防潮: { zh: '防潮', en: 'Keep dry', ru: 'Беречь от влаги' },
  禁止堆叠: { zh: '禁止堆叠', en: 'Do not stack', ru: 'Не штабелировать' },
}

const COUNTRIES: Record<string, Triple> = {
  CN: { zh: '中国', en: 'China', ru: 'Китай' },
  KZ: { zh: '哈萨克斯坦', en: 'Kazakhstan', ru: 'Казахстан' },
  RU: { zh: '俄罗斯', en: 'Russia', ru: 'Россия' },
  KG: { zh: '吉尔吉斯斯坦', en: 'Kyrgyzstan', ru: 'Кыргызстан' },
  UZ: { zh: '乌兹别克斯坦', en: 'Uzbekistan', ru: 'Узбекистан' },
}

say('新报价待确认', 'New quote awaiting confirmation', 'Новая ставка ждёт подтверждения')
say('乌鲁木齐 → 阿拉木图，3 名司机关注本票，最低已到货主底价附近。', 'Urumqi → Almaty: 3 drivers watching this load; the lowest quote is near the floor.', 'Урумчи → Алматы: 3 водителя следят за грузом, минимум около нижней цены.')
say('待签收运单', 'Waybill awaiting signature', 'Накладная ждёт подписи')
say('电子运单已生成，请核对件数后签字。', 'The e-waybill is ready. Check the piece count and sign.', 'Электронная накладная готова. Сверьте число мест и подпишите.')
say('霍尔果斯排队回落', 'Khorgos queue easing', 'Очередь в Хоргосе снижается')
say('当前约 70 分钟，适合今晚发车。', 'About 70 minutes now; good for tonight’s departure.', 'Около 70 минут, удобно выезжать сегодня вечером.')
say('当前约 70 分钟，上报可积口岸分。', 'About 70 minutes now. Reporting adds border points.', 'Около 70 минут. Сообщение даёт баллы КПП.')
say('保证金冻结 ¥200', 'Deposit frozen ¥200', 'Депозит заморожен ¥200')
say('成交后冻结，签收完成自动解冻。', 'Frozen after the deal; auto-unfrozen on sign-off.', 'Заморозка после сделки, разморозка после подписи.')
say('企业证件在有效期内', 'Company papers still valid', 'Документы компании действительны')
say('营业执照与授权书无需重复提交。', 'Business license and authorization need not be resubmitted.', 'Лицензию и доверенность повторно подавать не нужно.')
say('奎屯 → 阿斯塔纳 新货源', 'New load: Kuitun → Astana', 'Новый груз: Куйтүн → Астана')
say('13.5 米厢货，抢单价已公布。', '13.5 m van; grab price posted.', 'Фургон 13.5 м, цена захвата опубликована.')
say('历史运单已评价', 'Past waybill reviewed', 'Прошлая накладная оценена')
say('货主给出 5 星，信用 +2。', 'Shipper gave 5 stars; credit +2.', 'Отправитель поставил 5 звёзд, рейтинг +2.')
say('绿卡有效期正常', 'Green card still valid', 'Зелёная карта действительна')
say('乌鲁木齐海关备案至 2027-06-30。', 'Filed with Urumqi Customs until 2027-06-30.', 'Учёт в таможне Урумчи до 2027-06-30.')
say('乌鲁木齐海关备案至 2027-06-30，续期入口在资质中心。', 'Filed with Urumqi Customs until 2027-06-30. Renew in KYC.', 'Учёт в таможне Урумчи до 2027-06-30. Продление — в KYC.')
say('指派邀请待处理', 'Assignment invite pending', 'Приглашение ждёт ответа')
say('优先走霍尔果斯，请 24 小时内确认。', 'Prefer Khorgos. Confirm within 24 hours.', 'Предпочтительно Хоргос. Подтвердите за 24 часа.')
say('阿拉山口通关正常', 'Alashankou clearance normal', 'Алашанькоу работает нормально')
say('换装约 40 分钟，上报可积口岸分。', 'Transshipment about 40 minutes. Reporting adds border points.', 'Перегрузка около 40 минут. Сообщение даёт баллы КПП.')
say('库尔勒 → 阿拉木图 运输中', 'Korla → Almaty in transit', 'Корла → Алматы в пути')
say('已过霍尔果斯，预计今晚抵达阿拉木图货站。', 'Passed Khorgos; due at Almaty depot tonight.', 'Прошли Хоргос, сегодня вечером на складе Алматы.')
say('乌鲁木齐 → 阿拉木图 新货源', 'New load: Urumqi → Almaty', 'Новый груз: Урумчи → Алматы')
say('13.5 米厢货，抢单价 ¥18,500。', '13.5 m van; grab price ¥18,500.', 'Фургон 13.5 м, цена захвата ¥18,500.')
say('司机已抢单，请在 30 分钟内确认', 'Driver grabbed the load. Confirm within 30 minutes.', 'Водитель взял груз. Подтвердите за 30 минут.')
say('乌鲁木齐 → 阿拉木图，努尔兰·别科夫 · 信用 120。', 'Urumqi → Almaty, Nurlan Bekov · credit 120.', 'Урумчи → Алматы, Нурлан Беков · рейтинг 120.')
say('电子运单待签收', 'E-waybill awaiting sign-off', 'Электронная накладная ждёт подписи')
say('ord_waitc_01 已送达，请核对件数后签字。', 'ord_waitc_01 delivered. Check the piece count and sign.', 'ord_waitc_01 доставлен. Сверьте число мест и подпишите.')
say('成交单 ord_transit_demo，解冻随签收完成。', 'Deal ord_transit_demo; unfreeze after sign-off.', 'Сделка ord_transit_demo; разморозка после подписи.')
say('可走霍尔果斯，预计 36 小时', 'Can go via Khorgos, about 36 hours', 'Можно через Хоргос, около 36 часов')
say('有 17.5 米厢货，今晚可装', 'Have a 17.5 m van; can load tonight', 'Есть фургон 17.5 м, погрузка сегодня вечером')
say('绿卡有效，熟悉阿拉山口换装', 'Green card valid; know Alashankou transfer', 'Зелёная карта действительна, знаю перегрузку Алашанькоу')
say('冷链不断电，温度可追溯', 'Reefer stays powered; temperature is traceable', 'Рефрижератор без отключения, температура прослеживается')
say('已订口岸短驳，明早报关', 'Shuttle booked; customs in the morning', 'Шаттл заказан, таможня утром')
say('按随车清单交接', 'Handover by packing list', 'Сдача по сопроводительному списку')
say('按随车清单交接，口岸换装提前 2 小时到达', 'Handover by packing list; arrive 2 hours early for border transfer', 'Сдача по списку; прибыть за 2 часа до перегрузки')
say('防潮，装卸需叉车，不可叠压', 'Keep dry; forklift required; do not crush', 'Беречь от влаги, нужна погрузка вилочным, не придавливать')
say('纸箱托盘，禁抛摔', 'Cartons on pallets; no throwing', 'Коробки на паллетах, не бросать')
say('防潮防污，车厢需干燥', 'Keep dry and clean; dry trailer', 'Беречь от влаги и грязи, кузов сухой')
say('防震防静电，禁止重压', 'Shock and static protection; no heavy stacking', 'Защита от удара и статики, не придавливать')
say('超长件提前沟通，绑扎加固', 'Advise overlength in advance; lash and brace', 'Длиномер согласовать заранее, крепление обязательно')
say('全程不断电，厢温 -18℃', 'Power on throughout; trailer -18°C', 'Без отключения питания, -18°C в кузове')
say('原厂木箱，禁倒置', 'OEM crates; do not invert', 'Заводские ящики, не переворачивать')
say('直立摆放，禁压顶', 'Stand upright; do not stack on top', 'Ставить вертикально, не ставить сверху')
say('超长捆扎，装卸需吊具', 'Overlength lashing; lifting gear required', 'Длиномер крепить, нужна такелажная техника')
say('通风保鲜，禁与气味货混装', 'Ventilate; do not mix with odorous cargo', 'Вентиляция, не смешивать с пахучим грузом')
say('原厂纸箱直立，禁止倒置', 'OEM cartons upright; do not invert', 'Заводские коробки вертикально, не переворачивать')
say('立放码垛，防油污', 'Stand and stack; keep oil off', 'Ставить вертикально, беречь от масла')
say('防潮防霉，车厢保持干燥', 'Keep dry against mold; dry trailer', 'Беречь от влаги и плесени, кузов сухой')
say('请按随车清单清点，口岸换装后拍照确认。', 'Count by packing list and photo after border transfer.', 'Сверьте по списку и сфотографируйте после перегрузки.')
say('收到，已过霍尔果斯，预计今晚抵达。', 'Copy. Passed Khorgos, arriving tonight.', 'Принято. Прошли Хоргос, прибытие сегодня вечером.')
say('已到达霍尔果斯', 'Arrived at Khorgos', 'Прибыли в Хоргос')
say('请注意口岸拥堵，霍尔果斯目前排队约 3 小时', 'Border congestion: Khorgos queue about 3 hours', 'Затор на КПП: очередь в Хоргосе около 3 часов')
say('准时到达，车况干净，配合卸货', 'On time, clean truck, helped with unloading', 'Вовремя, чистая машина, помог на разгрузке')
say('货损，箱体进水', 'Cargo damage, water in the box', 'Порча груза, вода в кузове')
say('超时未装货', 'Loading overdue', 'Погрузка просрочена')
say('箱体进水照片，底部托盘受潮', 'Photo of water in the box; bottom pallet wet', 'Фото воды в кузове, нижний паллет влажный')
say('装货时车厢干燥', 'Trailer was dry at loading', 'При погрузке кузов был сухой')
say('累计违约 3 次', '3 contract breaches', '3 нарушения договора')
say('货源虚假联系方式', 'Fake contact on the load', 'Ложный контакт в заявке')
say('绿卡过期仍接单', 'Took orders with an expired green card', 'Брал заказы с просроченной зелёной картой')
say('保证金流水异常', 'Abnormal deposit ledger', 'Аномалия по депозиту')
say('某车队', 'A fleet', 'Автопарк')
say('空号货主', 'Fake shipper', 'Фиктивный отправитель')
say('过期绿卡承运', 'Expired green-card carrier', 'Перевозчик с просроченной картой')
say('重复支付账户', 'Duplicate pay account', 'Дубль платёжного счёта')
say('阿克托雷·仓库', 'Aktore warehouse', 'Склад Акторе')
say('Рахимов 收货', 'Rakhimov receiving', 'Рахимов, приёмка')
say('Ош 货站 阿地力', 'Osh depot Adil', 'Грузовой двор Ош, Адыл')
say('Бишкек 物流园', 'Bishkek logistics park', 'Логистический парк Бишкек')
say('Астана 冷库值班', 'Astana cold store desk', 'Холодильник Астана')
say('Шымкент 建材仓', 'Shymkent materials warehouse', 'Склад стройматериалов Шымкент')
say('Тараз 接货点', 'Taraz receiving point', 'Пункт приёмки Тараз')
say('Новосибирск 仓 彼得罗娃', 'Novosibirsk warehouse Petrova', 'Склад Новосибирск, Петрова')
say('Москва 仓 Петрова', 'Moscow warehouse Petrova', 'Склад Москва, Петрова')
say('Достык 换装场', 'Dostyk transshipment yard', 'Перегрузка Достык')
say('Талдыкорган 站台', 'Taldykorgan platform', 'Платформа Талдыкорган')
say('Нарын 接货', 'Naryn receiving', 'Приёмка Нарын')
say('Андижан 货场', 'Andijan yard', 'Двор Андижан')
say('СПб 仓 伊万诺夫', 'St. Petersburg warehouse Ivanov', 'Склад СПб, Иванов')
say('Казань 物流园', 'Kazan logistics park', 'Логистический парк Казань')
say('Екб 货站', 'Yekaterinburg depot', 'Грузовой двор Екатеринбург')
say('Омск 接货点', 'Omsk receiving point', 'Пункт приёмки Омск')
say('优先走霍尔果斯', 'Prefer Khorgos', 'Предпочтительно Хоргос')
say('霍尔果斯拥堵', 'Khorgos congestion', 'Затор в Хоргосе')
say('预计等待 3 小时', 'Expect a 3-hour wait', 'Ожидание около 3 часов')
say('货主', 'Shipper', 'Отправитель')
say('司机', 'Driver', 'Водитель')
say('Khorgos congestion', 'Khorgos congestion', 'Затор в Хоргосе')
say('Expect 3h wait', 'Expect a 3-hour wait', 'Ожидание около 3 часов')

export const ORIGIN_CITIES = ['乌鲁木齐', '霍尔果斯', '喀什', '阿拉山口', '奎屯', '伊宁', '库尔勒', '哈密', '昌吉', '石河子']
export const DEST_CITIES = ['阿拉木图', '奥什', '多斯特克', '比什凯克', '阿斯塔纳', '莫斯科', '塔什干', '新西伯利亚', '圣彼得堡', '奇姆肯特', '塔拉兹', '安集延', '塔尔迪库尔干']
export const CARGO_OPTIONS = Object.keys(CARGOS).filter((k) => /[\u4e00-\u9fff]/.test(k))

const PLACE_ALIAS = new Map<string, string>()
for (const [key, row] of Object.entries(PLACES)) {
  PLACE_ALIAS.set(key, key)
  PLACE_ALIAS.set(row.zh, key)
  PLACE_ALIAS.set(row.en.toLowerCase(), key)
  PLACE_ALIAS.set(row.ru.toLowerCase(), key)
}

export function canonPlace(name: unknown): string {
  const s = String(name || '').trim()
  return PLACE_ALIAS.get(s) || PLACE_ALIAS.get(s.toLowerCase()) || s
}

export function place(name: unknown): string {
  const s = canonPlace(name)
  return pick(PLACES[s], s)
}

export function company(name: unknown): string {
  const s = String(name || '').trim()
  return pick(lookup(COMPANIES, s), s)
}

/** 人名只做音译，不走公司词典，避免「家居」变成家具。 */
export function party(name: unknown): string {
  const s = String(name || '').trim()
  return pick(lookup(PEOPLE, s), s)
}

/** 人名字段和公司字段混用时：先人名音译，再公司音译。 */
export function entity(name: unknown): string {
  const s = String(name || '').trim()
  if (!s) return ''
  return pick(lookup(PEOPLE, s) || lookup(COMPANIES, s) || lookup(PHRASES, s), s)
}

export function customs(name: unknown): string {
  const s = String(name || '').trim()
  return pick(lookup(CUSTOMS, s), s)
}

export function brand(name: unknown): string {
  const s = String(name || '').trim()
  return pick(lookup(BRANDS, s), s)
}

const REPLACE_TABLE: Array<[string, Triple]> = (() => {
  const rows: Array<[string, Triple]> = []
  const seen = new Set<string>()
  const add = (key: string, row: Triple) => {
    if (!key || seen.has(key)) return
    seen.add(key)
    rows.push([key, row])
  }
  for (const [k, row] of Object.entries(PHRASES)) add(k, row)
  for (const [k, row] of Object.entries(COMPANIES)) add(k, row)
  for (const [k, row] of Object.entries(PEOPLE)) add(k, row)
  for (const [k, row] of Object.entries(CUSTOMS)) add(k, row)
  for (const [k, row] of Object.entries(BRANDS)) add(k, row)
  for (const [k, row] of Object.entries(CARGOS)) add(k, row)
  for (const [k, row] of Object.entries(PLACES)) add(k, row)
  rows.sort((a, b) => b[0].length - a[0].length)
  return rows
})()

export function phrase(raw: unknown): string {
  const s = String(raw || '').trim()
  if (!s) return ''
  const exact = lookup(PHRASES, s) || lookup(REMARKS, s) || lookup(PEOPLE, s) || lookup(COMPANIES, s) || lookup(CUSTOMS, s) || lookup(BRANDS, s)
  if (exact) return pick(exact, s)
  let out = s
  for (const [key, row] of REPLACE_TABLE) {
    if (key.length < 2) continue
    if (out.includes(key)) out = out.split(key).join(pick(row, key))
  }
  return out
}

export function laneText(lane: unknown): string {
  return String(lane || '')
    .split('→')
    .map((part) => place(part.trim()))
    .join(' → ')
}

export function cargo(name: unknown): string {
  const s = String(name || '').trim()
  return pick(CARGOS[s], s)
}

export function packing(name: unknown): string {
  const s = String(name || '').trim()
  return pick(PACKING[s], s)
}

export function cargoClass(name: unknown): string {
  const s = String(name || '').trim()
  return pick(CLASSES[s], s)
}

export function remarkText(name: unknown): string {
  const s = String(name || '').trim()
  const hit = lookup(REMARKS, s) || lookup(PHRASES, s)
  if (hit) return pick(hit, s)
  return phrase(s)
}

export function countryName(code: unknown): string {
  const s = String(code || '').trim()
  return pick(COUNTRIES[s], s)
}

export function portName(p?: { nameZh?: string; nameEn?: string; nameRu?: string } | null): string {
  locale.value
  if (!p) return ''
  if (locale.value === 'en-US') return p.nameEn || p.nameZh || ''
  if (locale.value === 'ru-RU') return p.nameRu || p.nameEn || p.nameZh || ''
  return p.nameZh || p.nameEn || ''
}
