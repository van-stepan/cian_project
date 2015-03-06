# -*- coding: utf-8 -*-


# metro_station_districts = {
#                            
# u'аэропорт':'САО',
# u'беговая':'САО',
# u'водный стадион':'САО',
# u'войковская':'САО',
# u'динамо':'САО',
# u'полежаевская':'САО',
# u'петровско-разумовская':'САО',
# u'речной вокзал':'САО',
# u'сокол':'САО',
# u'тимирязевская':'САО',
# 
# u'волоколамская':'СЗАО',
# u'митино':'СЗАО',
# u'мякинино':'СЗАО',
# u'октябрьское поле':'СЗАО',
# u'планерная':'СЗАО',
# u'пятницкое шоссе':'СЗАО',
# u'сходненская':'СЗАО',
# u'строгино':'СЗАО',
# u'тушинская':'СЗАО',
# u'щукинская':'СЗАО',
# 
# u'багратионовская':'ЗАО',
# u'киевская':'ЗАО',
# u'кунцевская':'ЗАО',
# u'кутузовская':'ЗАО',
# u'крылатское':'ЗАО',
# u'молодежная':'ЗАО',
# u'парк победы':'ЗАО',
# u'пионерская':'ЗАО',
# u'проспект вернадского':'ЗАО',
# u'студенческая':'ЗАО',
# u'фили':'ЗАО',
# u'филевский парк':'ЗАО',
# u'юго-западная':'ЗАО',
# u'тропарево':'ЗАО',
# 
# u'академическая':'ЮЗАО',
# u'беляево':'ЮЗАО',
# u'битцевский парк':'ЮЗАО',
# u'дмитрия донского бульвар':'ЮЗАО',
# u'калужская':'ЮЗАО',
# u'каховская':'ЮЗАО',
# u'коньково':'ЮЗАО',
# u'ленинский проспект':'ЮЗАО',
# u'нахимовский проспект':'ЮЗАО',
# u'новые черемушки':'ЮЗАО',
# u'профсоюзная':'ЮЗАО',
# u'севастопольская':'ЮЗАО',
# u'теплый стан':'ЮЗАО',
# u'университет':'ЮЗАО',
# u'чертановская':'ЮЗАО',
# u'ясенево':'ЮЗАО',              
# u'новоясеневская':'ЮЗАО',
# 
# u'автозаводская':'ЮАО',
# u'ул. академика янгеля':'ЮАО',
# u'алма-атинская':'ЮАО',
# u'аннино':'ЮАО',
# u'варшавская':'ЮАО',
# u'домодедовская':'ЮАО',
# u'кантемировская':'ЮАО',
# u'каширская':'ЮАО',
# u'красногвардейская':'ЮАО',
# u'коломенская':'ЮАО',
# u'нагатинская':'ЮАО',
# u'нагорная':'ЮАО',
# u'орехово':'ЮАО',
# u'пражская':'ЮАО',
# u'тульская':'ЮАО',
# u'царицыно':'ЮАО',
# u'шаболовская':'ЮАО',
# u'южная':'ЮАО',
# 
# u'авиамоторная':'ЮВАО',
# u'братиславская':'ЮВАО',
# u'волжская':'ЮВАО',
# u'волгоградский проспект':'ЮВАО',
# u'дубровка':'ЮВАО',
# u'кузьминки':'ЮВАО',
# u'кожуховская':'ЮВАО',
# u'люблино':'ЮВАО',
# u'марьино':'ЮВАО',
# u'печатники':'ЮВАО',
# u'рязанский проспект':'ЮВАО',
# u'текстильщики':'ЮВАО',
# 
# u'выхино':'ВАО',
# u'измайловская':'ВАО',
# u'измайловский парк':'ВАО',
# u'новогиреево':'ВАО',
# u'первомайская':'ВАО',
# u'перово':'ВАО',
# u'преображенская площадь':'ВАО',
# u'семеновская':'ВАО',
# u'сокольники':'ВАО',
# u'улица подбельского':'ВАО',
# u'черкизовская':'ВАО',
# u'шоссе энтузиастов':'ВАО',
# u'щелковская':'ВАО',
# u'электрозаводская':'ВАО',
# 
# u'алексеевская':'CВАО',
# u'алтуфьево':'CВАО',
# u'бабушкинская':'CВАО',
# u'бибирево':'CВАО',
# u'ботанический Сад':'CВАО',
# u'вднх':'CВАО',
# u'владыкино':'CВАО',
# u'дмитровская':'CВАО',
# u'медведково':'CВАО',
# u'отрадное':'CВАО',
# u'свиблово':'CВАО',
# u'савеловская':'CВАО',
# 
# u'александровский сад':'ЦАО',
# u'арбатская':'ЦАО',
# u'баррикадная':'ЦАО',
# u'бауманская':'ЦАО',
# u'белорусская':'ЦАО',
# u'библиотека им. ленина':'ЦАО',
# u'боровицкая':'ЦАО',
# u'воробьевы горы':'ЦАО',
# u'добрынинская':'ЦАО',
# u'китай-город':'ЦАО',
# u'комсомольская':'ЦАО',
# u'красносельская':'ЦАО',
# u'краснопресненская':'ЦАО',
# u'красные ворота':'ЦАО',
# u'кропоткинская':'ЦАО',
# u'кузнецкий мост':'ЦАО',
# u'курская':'ЦАО',
# u'лубянка':'ЦАО',
# u'марксистская':'ЦАО',
# u'маяковская':'ЦАО',
# u'менделеевская':'ЦАО',
# u'новокузнецкая':'ЦАО',
# u'новослободская':'ЦАО',
# u'октябрьская':'ЦАО',
# u'охотный ряд':'ЦАО',
# u'павелецкая':'ЦАО',
# u'парк культуры':'ЦАО',
# u'пролетарская':'ЦАО',
# u'проспект мира':'ЦАО',
# u'площадь ильича':'ЦАО',
# u'площадь революции':'ЦАО',
# u'полянка':'ЦАО',
# u'пушкинская':'ЦАО',
# u'рижская':'ЦАО',
# u'серпуховская':'ЦАО',
# u'сухаревская':'ЦАО',
# u'смоленская':'ЦАО',
# u'спортивная':'ЦАО',
# u'таганская':'ЦАО',
# u'театральная':'ЦАО',
# u'тверская':'ЦАО',
# u'третьяковская':'ЦАО',
# u'трубная':'ЦАО',
# u'тургеневская':'ЦАО',
# u'улица 1905 года':'ЦАО',
# u'фрунзенская':'ЦАО',
# u'цветной бульвар':'ЦАО',
# u'чистые пруды':'ЦАО',
# u'чеховская':'ЦАО'
# 
# }

metro_station_districts = [

        ['аэропорт', 'САО'],
        ['беговая', 'САО'],
        ['водный стадион', 'САО'],
        ['войковская', 'САО'],
        ['динамо', 'САО'],
        ['полежаевская', 'САО'],
        ['петровско-разумовская', 'САО'],
        ['речной вокзал', 'САО'],
        ['сокол', 'САО'],
        ['тимирязевская', 'САО'],
        
        ['волоколамская', 'СЗАО'],
        ['митино', 'СЗАО'],
        ['мякинино', 'СЗАО'],
        ['октябрьское поле', 'СЗАО'],
        ['планерная', 'СЗАО'],
        ['пятницкое шоссе', 'СЗАО'],
        ['сходненская', 'СЗАО'],
        ['строгино', 'СЗАО'],
        ['тушинская', 'СЗАО'],
        ['щукинская', 'СЗАО'],
        
        ['багратионовская', 'ЗАО'],
        ['киевская', 'ЗАО'],
        ['кунцевская', 'ЗАО'],
        ['кутузовская', 'ЗАО'],
        ['крылатское', 'ЗАО'],
        ['молодежная', 'ЗАО'],
        ['парк победы', 'ЗАО'],
        ['пионерская', 'ЗАО'],
        ['проспект вернадского', 'ЗАО'],
        ['студенческая', 'ЗАО'],
        ['фили', 'ЗАО'],
        ['филевский парк', 'ЗАО'],
        ['юго-западная', 'ЗАО'],
        ['тропарево', 'ЗАО'],
        
        ['академическая', 'ЮЗАО'],
        ['беляево', 'ЮЗАО'],
        ['битцевский парк', 'ЮЗАО'],
        ['дмитрия донского бульвар', 'ЮЗАО'],
        ['калужская', 'ЮЗАО'],
        ['каховская', 'ЮЗАО'],
        ['коньково', 'ЮЗАО'],
        ['ленинский проспект', 'ЮЗАО'],
        ['нахимовский проспект', 'ЮЗАО'],
        ['новые черемушки', 'ЮЗАО'],
        ['профсоюзная', 'ЮЗАО'],
        ['севастопольская', 'ЮЗАО'],
        ['теплый стан', 'ЮЗАО'],
        ['университет', 'ЮЗАО'],
        ['чертановская', 'ЮЗАО'],
        ['ясенево', 'ЮЗАО'],              
        ['новоясеневская', 'ЮЗАО'],
        
        ['автозаводская', 'ЮАО'],
        ['ул. академика янгеля', 'ЮАО'],
        ['алма-атинская', 'ЮАО'],
        ['аннино', 'ЮАО'],
        ['варшавская', 'ЮАО'],
        ['домодедовская', 'ЮАО'],
        ['кантемировская', 'ЮАО'],
        ['каширская', 'ЮАО'],
        ['красногвардейская', 'ЮАО'],
        ['коломенская', 'ЮАО'],
        ['нагатинская', 'ЮАО'],
        ['нагорная', 'ЮАО'],
        ['орехово', 'ЮАО'],
        ['пражская', 'ЮАО'],
        ['тульская', 'ЮАО'],
        ['царицыно', 'ЮАО'],
        ['шаболовская', 'ЮАО'],
        ['южная', 'ЮАО'],
        
        ['авиамоторная', 'ЮВАО'],
        ['братиславская', 'ЮВАО'],
        ['волжская', 'ЮВАО'],
        ['волгоградский проспект', 'ЮВАО'],
        ['дубровка', 'ЮВАО'],
        ['кузьминки', 'ЮВАО'],
        ['кожуховская', 'ЮВАО'],
        ['люблино', 'ЮВАО'],
        ['марьино', 'ЮВАО'],
        ['печатники', 'ЮВАО'],
        ['рязанский проспект', 'ЮВАО'],
        ['текстильщики', 'ЮВАО'],
        
        ['выхино', 'ВАО'],
        ['измайловская', 'ВАО'],
        ['измайловский парк', 'ВАО'],
        ['новогиреево', 'ВАО'],
        ['первомайская', 'ВАО'],
        ['перово', 'ВАО'],
        ['преображенская площадь', 'ВАО'],
        ['семеновская', 'ВАО'],
        ['сокольники', 'ВАО'],
        ['улица подбельского', 'ВАО'],
        ['черкизовская', 'ВАО'],
        ['шоссе энтузиастов', 'ВАО'],
        ['щелковская', 'ВАО'],
        ['электрозаводская', 'ВАО'],
        
        ['алексеевская', 'CВАО'],
        ['алтуфьево', 'CВАО'],
        ['бабушкинская', 'CВАО'],
        ['бибирево', 'CВАО'],
        ['ботанический Сад', 'CВАО'],
        ['вднх', 'CВАО'],
        ['владыкино', 'CВАО'],
        ['дмитровская', 'CВАО'],
        ['медведково', 'CВАО'],
        ['отрадное', 'CВАО'],
        ['свиблово', 'CВАО'],
        ['савеловская', 'CВАО'],
        
        ['александровский сад', 'ЦАО'],
        ['арбатская', 'ЦАО'],
        ['баррикадная', 'ЦАО'],
        ['бауманская', 'ЦАО'],
        ['белорусская', 'ЦАО'],
        ['библиотека им. ленина', 'ЦАО'],
        ['боровицкая', 'ЦАО'],
        ['воробьевы горы', 'ЦАО'],
        ['добрынинская', 'ЦАО'],
        ['китай-город', 'ЦАО'],
        ['комсомольская', 'ЦАО'],
        ['красносельская', 'ЦАО'],
        ['краснопресненская', 'ЦАО'],
        ['красные ворота', 'ЦАО'],
        ['кропоткинская', 'ЦАО'],
        ['кузнецкий мост', 'ЦАО'],
        ['курская', 'ЦАО'],
        ['лубянка', 'ЦАО'],
        ['марксистская', 'ЦАО'],
        ['маяковская', 'ЦАО'],
        ['менделеевская', 'ЦАО'],
        ['новокузнецкая', 'ЦАО'],
        ['новослободская', 'ЦАО'],
        ['октябрьская', 'ЦАО'],
        ['охотный ряд', 'ЦАО'],
        ['павелецкая', 'ЦАО'],
        ['парк культуры', 'ЦАО'],
        ['пролетарская', 'ЦАО'],
        ['проспект мира', 'ЦАО'],
        ['площадь ильича', 'ЦАО'],
        ['площадь революции', 'ЦАО'],
        ['полянка', 'ЦАО'],
        ['пушкинская', 'ЦАО'],
        ['рижская', 'ЦАО'],
        ['серпуховская', 'ЦАО'],
        ['сухаревская', 'ЦАО'],
        ['смоленская', 'ЦАО'],
        ['спортивная', 'ЦАО'],
        ['таганская', 'ЦАО'],
        ['театральная', 'ЦАО'],
        ['тверская', 'ЦАО'],
        ['третьяковская', 'ЦАО'],
        ['трубная', 'ЦАО'],
        ['тургеневская', 'ЦАО'],
        ['улица 1905 года', 'ЦАО'],
        ['фрунзенская', 'ЦАО'],
        ['цветной бульвар', 'ЦАО'],
        ['чистые пруды', 'ЦАО'],
        ['чеховская', 'ЦАО']

]


def getDistrictByMetroStation(metro):
    
    metro = metro.lower()
    
    for item in metro_station_districts:
        if item[0].find(metro) != -1:
            return item[1]
    
    return "."
        
    
    


metro_stations = [[1, '85', '\xd0\x90\xd0\xb2\xd0\xb8\xd0\xb0\xd0\xbc\xd0\xbe\xd1\x82\xd0\xbe\xd1\x80\xd0\xbd\xd0\xb0\xd1\x8f', 'metro_select', '37.717052 55.751558'], 
[2, '13', '\xd0\x90\xd0\xb2\xd1\x82\xd0\xbe\xd0\xb7\xd0\xb0\xd0\xb2\xd0\xbe\xd0\xb4\xd1\x81\xd0\xba\xd0\xb0\xd1\x8f', 'metro_select', '37.657440 55.707167'], 
[3, '97', '\xd0\x90\xd0\xba\xd0\xb0\xd0\xb4\xd0\xb5\xd0\xbc\xd0\xb8\xd1\x87\xd0\xb5\xd1\x81\xd0\xba\xd0\xb0\xd1\x8f', 'metro_select', '37.573555 55.687868'], 
[4, '53', '\xd0\x90\xd0\xbb\xd0\xb5\xd0\xba\xd1\x81\xd0\xb0\xd0\xbd\xd0\xb4\xd1\x80\xd0\xbe\xd0\xb2\xd1\x81\xd0\xba\xd0\xb8\xd0\xb9 \xd1\x81\xd0\xb0\xd0\xb4', 'metro_select', '37.610009 55.752298'], 
[5, '105', '\xd0\x90\xd0\xbb\xd0\xb5\xd0\xba\xd1\x81\xd0\xb5\xd0\xb5\xd0\xb2\xd1\x81\xd0\xba\xd0\xb0\xd1\x8f', 'metro_select', '37.638979 55.808295'], 
[6, '213', '\xd0\x90\xd0\xbb\xd0\xbc\xd0\xb0-\xd0\x90\xd1\x82\xd0\xb8\xd0\xbd\xd1\x81\xd0\xba\xd0\xb0\xd1\x8f', 'metro_select', '37.765678 55.63349'], 
[7, '135', '\xd0\x90\xd0\xbb\xd1\x82\xd1\x83\xd1\x84\xd1\x8c\xd0\xb5\xd0\xb2\xd0\xbe', 'metro_select', '37.587128 55.897912'], 
[8, '156', '\xd0\x90\xd0\xbd\xd0\xbd\xd0\xb8\xd0\xbd\xd0\xbe', 'metro_select', '37.596830 55.583250'], 
[9, '50', '\xd0\x90\xd1\x80\xd0\xb1\xd0\xb0\xd1\x82\xd1\x81\xd0\xba\xd0\xb0\xd1\x8f', 'metro_select', '37.601753 55.752404'], 
[10, '5', '\xd0\x90\xd1\x8d\xd1\x80\xd0\xbe\xd0\xbf\xd0\xbe\xd1\x80\xd1\x82', 'metro_select', '37.533706 55.800812'], 
[11, '109', '\xd0\x91\xd0\xb0\xd0\xb1\xd1\x83\xd1\x88\xd0\xba\xd0\xb8\xd0\xbd\xd1\x81\xd0\xba\xd0\xb0\xd1\x8f', 'metro_select', '37.664150 55.869602'], 
[12, '57', '\xd0\x91\xd0\xb0\xd0\xb3\xd1\x80\xd0\xb0\xd1\x82\xd0\xb8\xd0\xbe\xd0\xbd\xd0\xbe\xd0\xb2\xd1\x81\xd0\xba\xd0\xb0\xd1\x8f', 'metro_select', '37.497710 55.743735'], 
[13, '71', '\xd0\x91\xd0\xb0\xd1\x80\xd1\x80\xd0\xb8\xd0\xba\xd0\xb0\xd0\xb4\xd0\xbd\xd0\xb0\xd1\x8f', 'metro_select', '37.581280 55.760803'], 
[14, '47', '\xd0\x91\xd0\xb0\xd1\x83\xd0\xbc\xd0\xb0\xd0\xbd\xd1\x81\xd0\xba\xd0\xb0\xd1\x8f', 'metro_select', '37.679520 55.772472'], 
[15, '69', '\xd0\x91\xd0\xb5\xd0\xb3\xd0\xbe\xd0\xb2\xd0\xb0\xd1\x8f', 'metro_select', '37.546821 55.773682'], 
[16, '7', '\xd0\x91\xd0\xb5\xd0\xbb\xd0\xbe\xd1\x80\xd1\x83\xd1\x81\xd1\x81\xd0\xba\xd0\xb0\xd1\x8f', 'metro_select', '37.582242 55.775717'], 
[17, '93', '\xd0\x91\xd0\xb5\xd0\xbb\xd1\x8f\xd0\xb5\xd0\xb2\xd0\xbe', 'metro_select', '37.526304 55.642464'], 
[18, '131', '\xd0\x91\xd0\xb8\xd0\xb1\xd0\xb8\xd1\x80\xd0\xb5\xd0\xb2\xd0\xbe', 'metro_select', '37.602687 55.884272'], 
[19, '30', '\xd0\x91\xd0\xb8\xd0\xb1\xd0\xbb\xd0\xb8\xd0\xbe\xd1\x82\xd0\xb5\xd0\xba\xd0\xb0 \xd0\x9b\xd0\xb5\xd0\xbd\xd0\xb8\xd0\xbd\xd0\xb0', 'metro_select', '37.610997 55.752698'], 
[20, '207', '\xd0\x91\xd0\xbe\xd1\x80\xd0\xb8\xd1\x81\xd0\xbe\xd0\xb2\xd0\xbe', 'metro_select', '37.742598 55.635400'], 
[21, '120', '\xd0\x91\xd0\xbe\xd1\x80\xd0\xbe\xd0\xb2\xd0\xb8\xd1\x86\xd0\xba\xd0\xb0\xd1\x8f', 'metro_select', '37.610152 55.751705'], 
[22, '107', '\xd0\x91\xd0\xbe\xd1\x82\xd0\xb0\xd0\xbd\xd0\xb8\xd1\x87\xd0\xb5\xd1\x81\xd0\xba\xd0\xb8\xd0\xb9 \xd1\x81\xd0\xb0\xd0\xb4', 'metro_select', '37.638225 55.845451'], 
[23, '145', '\xd0\x91\xd1\x80\xd0\xb0\xd1\x82\xd0\xb8\xd1\x81\xd0\xbb\xd0\xb0\xd0\xb2\xd1\x81\xd0\xba\xd0\xb0\xd1\x8f', 'metro_select', '37.750801 55.659500'], 
[24, '195', '\xd0\x91\xd1\x83\xd0\xbd\xd0\xb8\xd0\xbd\xd1\x81\xd0\xba\xd0\xb0\xd1\x8f \xd0\xb0\xd0\xbb\xd0\xbb\xd0\xb5\xd1\x8f', 'metro_select', '37.516781 55.537974'], 
[25, '106', '\xd0\x92\xd0\x94\xd0\x9d\xd0\xa5', 'metro_select', '37.641315 55.821032'], 
[26, '16', '\xd0\x92\xd0\xb0\xd1\x80\xd1\x88\xd0\xb0\xd0\xb2\xd1\x81\xd0\xba\xd0\xb0\xd1\x8f', 'metro_select', '37.619558 55.653492'], 
[27, '24', '\xd0\x92\xd0\xb5\xd1\x80\xd0\xbd\xd0\xb0\xd0\xb4\xd1\x81\xd0\xba\xd0\xbe\xd0\xb3\xd0\xbe \xd0\xbf\xd1\x80\xd0\xbe\xd1\x81\xd0\xbf\xd0\xb5\xd0\xba\xd1\x82', 'metro_select', '37.506091 55.676945'], 
[28, '112', '\xd0\x92\xd0\xbb\xd0\xb0\xd0\xb4\xd1\x8b\xd0\xba\xd0\xb8\xd0\xbd\xd0\xbe', 'metro_select', '37.589877 55.847280'], 
[29, '2', '\xd0\x92\xd0\xbe\xd0\xb4\xd0\xbd\xd1\x8b\xd0\xb9 \xd1\x81\xd1\x82\xd0\xb0\xd0\xb4\xd0\xb8\xd0\xbe\xd0\xbd', 'metro_select', '37.487128 55.839840'], 
[30, '3', '\xd0\x92\xd0\xbe\xd0\xb9\xd0\xba\xd0\xbe\xd0\xb2\xd1\x81\xd0\xba\xd0\xb0\xd1\x8f', 'metro_select', '37.497791 55.818923'], 
[31, '77', '\xd0\x92\xd0\xbe\xd0\xbb\xd0\xb3\xd0\xbe\xd0\xb3\xd1\x80\xd0\xb0\xd0\xb4\xd1\x81\xd0\xba\xd0\xb8\xd0\xb9 \xd0\xbf\xd1\x80\xd0\xbe\xd1\x81\xd0\xbf\xd0\xb5\xd0\xba\xd1\x82', 'metro_select', '37.686527 55.725275'], 
[32, '142', '\xd0\x92\xd0\xbe\xd0\xbb\xd0\xb6\xd1\x81\xd0\xba\xd0\xb0\xd1\x8f', 'metro_select', '37.752823 55.690755'], 
[33, '203', '\xd0\x92\xd0\xbe\xd0\xbb\xd0\xbe\xd0\xba\xd0\xbe\xd0\xbb\xd0\xb0\xd0\xbc\xd1\x81\xd0\xba\xd0\xb0\xd1\x8f', 'metro_select', '37.381810 55.835594'], 
[34, '157', '\xd0\x92\xd0\xbe\xd1\x80\xd0\xbe\xd0\xb1\xd1\x8c\xd0\xb5\xd0\xb2\xd1\x8b \xd0\xb3\xd0\xbe\xd1\x80\xd1\x8b', 'metro_select', '37.559137 55.710246'], 
[35, '198', '\xd0\x92\xd1\x8b\xd1\x81\xd1\x82\xd0\xb0\xd0\xb2\xd0\xbe\xd1\x87\xd0\xbd\xd0\xb0\xd1\x8f', 'metro_select', '37.542770 55.750195'], 
[36, '81', '\xd0\x92\xd1\x8b\xd1\x85\xd0\xb8\xd0\xbd\xd0\xbe', 'metro_select', '37.817807 55.715961'], 
[37, '6', '\xd0\x94\xd0\xb8\xd0\xbd\xd0\xb0\xd0\xbc\xd0\xbe', 'metro_select', '37.558230 55.789821'], 
[38, '115', '\xd0\x94\xd0\xbc\xd0\xb8\xd1\x82\xd1\x80\xd0\xbe\xd0\xb2\xd1\x81\xd0\xba\xd0\xb0\xd1\x8f', 'metro_select', '37.581200 55.807547'], 
[39, '132', '\xd0\x94\xd0\xbe\xd0\xb1\xd1\x80\xd1\x8b\xd0\xbd\xd0\xb8\xd0\xbd\xd1\x81\xd0\xba\xd0\xb0\xd1\x8f', 'metro_select', '37.622594 55.729057'], 
[40, '21', '\xd0\x94\xd0\xbe\xd0\xbc\xd0\xbe\xd0\xb4\xd0\xb5\xd0\xb4\xd0\xbe\xd0\xb2\xd1\x81\xd0\xba\xd0\xb0\xd1\x8f', 'metro_select', '37.719594 55.610956'], 
[41, '164', '\xd0\x94\xd0\xbe\xd0\xbd\xd1\x81\xd0\xba\xd0\xbe\xd0\xb3\xd0\xbe \xd0\x94\xd0\xbc\xd0\xb8\xd1\x82\xd1\x80\xd0\xb8\xd1\x8f \xd0\xb1\xd1\x83\xd0\xbb\xd1\x8c\xd0\xb2\xd0\xb0\xd1\x80', 'metro_select', '37.576367 55.569382'], 
[42, '205', '\xd0\x94\xd0\xbe\xd1\x81\xd1\x82\xd0\xbe\xd0\xb5\xd0\xb2\xd1\x81\xd0\xba\xd0\xb0\xd1\x8f', 'metro_select', '37.613737 55.781742'], 
[43, '140', '\xd0\x94\xd1\x83\xd0\xb1\xd1\x80\xd0\xbe\xd0\xb2\xd0\xba\xd0\xb0', 'metro_select', '37.677212 55.717274'], 
[44, '216', '\xd0\x96\xd1\x83\xd0\xbb\xd0\xb5\xd0\xb1\xd0\xb8\xd0\xbd\xd0\xbe', 'metro_select', '37.855123 55.684539'], 
[45, '209', '\xd0\x97\xd1\x8f\xd0\xb1\xd0\xbb\xd0\xb8\xd0\xba\xd0\xbe\xd0\xb2\xd0\xbe', 'metro_select', '37.744529 55.612307'], 
[46, '43', '\xd0\x98\xd0\xb7\xd0\xbc\xd0\xb0\xd0\xb9\xd0\xbb\xd0\xbe\xd0\xb2\xd1\x81\xd0\xba\xd0\xb0\xd1\x8f', 'metro_select', '37.781380 55.787680'], 
[47, '94', '\xd0\x9a\xd0\xb0\xd0\xbb\xd1\x83\xd0\xb6\xd1\x81\xd0\xba\xd0\xb0\xd1\x8f', 'metro_select', '37.540488 55.657134'], 
[48, '18', '\xd0\x9a\xd0\xb0\xd0\xbd\xd1\x82\xd0\xb5\xd0\xbc\xd0\xb8\xd1\x80\xd0\xbe\xd0\xb2\xd1\x81\xd0\xba\xd0\xb0\xd1\x8f', 'metro_select', '37.656613 55.635782'], 
[49, '17', '\xd0\x9a\xd0\xb0\xd1\x85\xd0\xbe\xd0\xb2\xd1\x81\xd0\xba\xd0\xb0\xd1\x8f', 'metro_select', '37.598286 55.652994'], 
[50, '15', '\xd0\x9a\xd0\xb0\xd1\x88\xd0\xb8\xd1\x80\xd1\x81\xd0\xba\xd0\xb0\xd1\x8f', 'metro_select', '37.648690 55.655239'], 
[51, '52', '\xd0\x9a\xd0\xb8\xd0\xb5\xd0\xb2\xd1\x81\xd0\xba\xd0\xb0\xd1\x8f', 'metro_select', '37.567312 55.744678'], 
[52, '74', '\xd0\x9a\xd0\xb8\xd1\x82\xd0\xb0\xd0\xb9-\xd0\xb3\xd0\xbe\xd1\x80\xd0\xbe\xd0\xb4', 'metro_select', '37.633823 55.755398'], 
[53, '144', '\xd0\x9a\xd0\xbe\xd0\xb6\xd1\x83\xd1\x85\xd0\xbe\xd0\xb2\xd1\x81\xd0\xba\xd0\xb0\xd1\x8f', 'metro_select', '37.685593 55.706203'], 
[54, '14', '\xd0\x9a\xd0\xbe\xd0\xbb\xd0\xbe\xd0\xbc\xd0\xb5\xd0\xbd\xd1\x81\xd0\xba\xd0\xb0\xd1\x8f', 'metro_select', '37.663889 55.678387'], 
[55, '35', '\xd0\x9a\xd0\xbe\xd0\xbc\xd1\x81\xd0\xbe\xd0\xbc\xd0\xbe\xd0\xbb\xd1\x8c\xd1\x81\xd0\xba\xd0\xb0\xd1\x8f', 'metro_select', '37.656029 55.774659'], 
[56, '92', '\xd0\x9a\xd0\xbe\xd0\xbd\xd1\x8c\xd0\xba\xd0\xbe\xd0\xb2\xd0\xbe', 'metro_select', '37.519360 55.633109'], 
[57, '22', '\xd0\x9a\xd1\x80\xd0\xb0\xd1\x81\xd0\xbd\xd0\xbe\xd0\xb3\xd0\xb2\xd0\xb0\xd1\x80\xd0\xb4\xd0\xb5\xd0\xb9\xd1\x81\xd0\xba\xd0\xb0\xd1\x8f', 'metro_select', '37.744522 55.614048'], 
[58, '133', '\xd0\x9a\xd1\x80\xd0\xb0\xd1\x81\xd0\xbd\xd0\xbe\xd0\xbf\xd1\x80\xd0\xb5\xd1\x81\xd0\xbd\xd0\xb5\xd0\xbd\xd1\x81\xd0\xba\xd0\xb0\xd1\x8f', 'metro_select', '37.577543 55.760596'], 
[59, '36', '\xd0\x9a\xd1\x80\xd0\xb0\xd1\x81\xd0\xbd\xd0\xbe\xd1\x81\xd0\xb5\xd0\xbb\xd1\x8c\xd1\x81\xd0\xba\xd0\xb0\xd1\x8f', 'metro_select', '37.666279 55.780117'], 
[60, '34', '\xd0\x9a\xd1\x80\xd0\xb0\xd1\x81\xd0\xbd\xd1\x8b\xd0\xb5 \xd0\xb2\xd0\xbe\xd1\x80\xd0\xbe\xd1\x82\xd0\xb0', 'metro_select', '37.649094 55.768876'], 
[61, '139', '\xd0\x9a\xd1\x80\xd0\xb5\xd1\x81\xd1\x82\xd1\x8c\xd1\x8f\xd0\xbd\xd1\x81\xd0\xba\xd0\xb0\xd1\x8f \xd0\xb7\xd0\xb0\xd1\x81\xd1\x82\xd0\xb0\xd0\xb2\xd0\xb0', 'metro_select', '37.665722 55.732448'], 
[62, '29', '\xd0\x9a\xd1\x80\xd0\xbe\xd0\xbf\xd0\xbe\xd1\x82\xd0\xba\xd0\xb8\xd0\xbd\xd1\x81\xd0\xba\xd0\xb0\xd1\x8f', 'metro_select', '37.602777 55.745144'], 
[63, '62', '\xd0\x9a\xd1\x80\xd1\x8b\xd0\xbb\xd0\xb0\xd1\x82\xd1\x81\xd0\xba\xd0\xbe\xd0\xb5', 'metro_select', '37.408130 55.756862'], 
[64, '73', '\xd0\x9a\xd1\x83\xd0\xb7\xd0\xbd\xd0\xb5\xd1\x86\xd0\xba\xd0\xb8\xd0\xb9 \xd0\xbc\xd0\xbe\xd1\x81\xd1\x82', 'metro_select', '37.624903 55.761259'], 
[65, '79', '\xd0\x9a\xd1\x83\xd0\xb7\xd1\x8c\xd0\xbc\xd0\xb8\xd0\xbd\xd0\xba\xd0\xb8', 'metro_select', '37.765417 55.705452'], 
[66, '60', '\xd0\x9a\xd1\x83\xd0\xbd\xd1\x86\xd0\xb5\xd0\xb2\xd1\x81\xd0\xba\xd0\xb0\xd1\x8f', 'metro_select', '37.446003 55.730791'], 
[67, '48', '\xd0\x9a\xd1\x83\xd1\x80\xd1\x81\xd0\xba\xd0\xb0\xd1\x8f', 'metro_select', '37.659928 55.758179'], 
[68, '55', '\xd0\x9a\xd1\x83\xd1\x82\xd1\x83\xd0\xb7\xd0\xbe\xd0\xb2\xd1\x81\xd0\xba\xd0\xb0\xd1\x8f', 'metro_select', '37.534173 55.739965'], 
[69, '98', '\xd0\x9b\xd0\xb5\xd0\xbd\xd0\xb8\xd0\xbd\xd1\x81\xd0\xba\xd0\xb8\xd0\xb9 \xd0\xbf\xd1\x80\xd0\xbe\xd1\x81\xd0\xbf\xd0\xb5\xd0\xba\xd1\x82', 'metro_select', '37.586158 55.707491'], 
[70, '215', '\xd0\x9b\xd0\xb5\xd1\x80\xd0\xbc\xd0\xbe\xd0\xbd\xd1\x82\xd0\xbe\xd0\xb2\xd1\x81\xd0\xba\xd0\xb8\xd0\xb9 \xd0\xbf\xd1\x80\xd0\xbe\xd1\x81\xd0\xbf\xd0\xb5\xd0\xba\xd1\x82', 'metro_select', '37.852275 55.701765'], 
[71, '32', '\xd0\x9b\xd1\x83\xd0\xb1\xd1\x8f\xd0\xbd\xd0\xba\xd0\xb0', 'metro_select', '37.625873 55.760150'], 
[72, '143', '\xd0\x9b\xd1\x8e\xd0\xb1\xd0\xbb\xd0\xb8\xd0\xbd\xd0\xbe', 'metro_select', '37.761473 55.675753'], 
[73, '87', '\xd0\x9c\xd0\xb0\xd1\x80\xd0\xba\xd1\x81\xd0\xb8\xd1\x81\xd1\x82\xd1\x81\xd0\xba\xd0\xb0\xd1\x8f', 'metro_select', '37.656577 55.741140'], 
[74, '204', '\xd0\x9c\xd0\xb0\xd1\x80\xd1\x8c\xd0\xb8\xd0\xbd\xd0\xb0 \xd1\x80\xd0\xbe\xd1\x89\xd0\xb0', 'metro_select', '37.61662 55.795449'], 
[75, '146', '\xd0\x9c\xd0\xb0\xd1\x80\xd1\x8c\xd0\xb8\xd0\xbd\xd0\xbe', 'metro_select', '37.743902 55.650150'], 
[76, '8', '\xd0\x9c\xd0\xb0\xd1\x8f\xd0\xba\xd0\xbe\xd0\xb2\xd1\x81\xd0\xba\xd0\xb0\xd1\x8f', 'metro_select', '37.597001 55.769433'], 
[77, '110', '\xd0\x9c\xd0\xb5\xd0\xb4\xd0\xb2\xd0\xb5\xd0\xb4\xd0\xba\xd0\xbe\xd0\xb2\xd0\xbe', 'metro_select', '37.661563 55.887215'], 
[78, '197', '\xd0\x9c\xd0\xb5\xd0\xb6\xd0\xb4\xd1\x83\xd0\xbd\xd0\xb0\xd1\x80\xd0\xbe\xd0\xb4\xd0\xbd\xd0\xb0\xd1\x8f', 'metro_select', '37.533454 55.748300'], 
[79, '117', '\xd0\x9c\xd0\xb5\xd0\xbd\xd0\xb4\xd0\xb5\xd0\xbb\xd0\xb5\xd0\xb5\xd0\xb2\xd1\x81\xd0\xba\xd0\xb0\xd1\x8f', 'metro_select', '37.599759 55.781529'], 
[80, '196', '\xd0\x9c\xd0\xb8\xd1\x82\xd0\xb8\xd0\xbd\xd0\xbe', 'metro_select', '37.354923 55.846113'], 
[81, '61', '\xd0\x9c\xd0\xbe\xd0\xbb\xd0\xbe\xd0\xb4\xd0\xb5\xd0\xb6\xd0\xbd\xd0\xb0\xd1\x8f', 'metro_select', '37.417050 55.740912'], 
[82, '202', '\xd0\x9c\xd1\x8f\xd0\xba\xd0\xb8\xd0\xbd\xd0\xb8\xd0\xbd\xd0\xbe', 'metro_select', '37.384738 55.82399'], 
[83, '124', '\xd0\x9d\xd0\xb0\xd0\xb3\xd0\xb0\xd1\x82\xd0\xb8\xd0\xbd\xd1\x81\xd0\xba\xd0\xb0\xd1\x8f', 'metro_select', '37.622127 55.683163'], 
[84, '125', '\xd0\x9d\xd0\xb0\xd0\xb3\xd0\xbe\xd1\x80\xd0\xbd\xd0\xb0\xd1\x8f', 'metro_select', '37.611122 55.673225'], 
[85, '126', '\xd0\x9d\xd0\xb0\xd1\x85\xd0\xb8\xd0\xbc\xd0\xbe\xd0\xb2\xd1\x81\xd0\xba\xd0\xb8\xd0\xb9 \xd0\xbf\xd1\x80\xd0\xbe\xd1\x81\xd0\xbf\xd0\xb5\xd0\xba\xd1\x82', 'metro_select', '37.605292 55.662654'], 
[86, '82', '\xd0\x9d\xd0\xbe\xd0\xb2\xd0\xbe\xd0\xb3\xd0\xb8\xd1\x80\xd0\xb5\xd0\xb5\xd0\xb2\xd0\xbe', 'metro_select', '37.816675 55.751867'], 
[87, '210', '\xd0\x9d\xd0\xbe\xd0\xb2\xd0\xbe\xd0\xba\xd0\xbe\xd1\x81\xd0\xb8\xd0\xbd\xd0\xbe', 'metro_select', '37.864149 55.744844'], 
[88, '11', '\xd0\x9d\xd0\xbe\xd0\xb2\xd0\xbe\xd0\xba\xd1\x83\xd0\xb7\xd0\xbd\xd0\xb5\xd1\x86\xd0\xba\xd0\xb0\xd1\x8f', 'metro_select', '37.629592 55.742134'], 
[89, '134', '\xd0\x9d\xd0\xbe\xd0\xb2\xd0\xbe\xd1\x81\xd0\xbb\xd0\xbe\xd0\xb1\xd0\xbe\xd0\xb4\xd1\x81\xd0\xba\xd0\xb0\xd1\x8f', 'metro_select', '37.601501 55.779707'], 
[90, '89', '\xd0\x9d\xd0\xbe\xd0\xb2\xd0\xbe\xd1\x8f\xd1\x81\xd0\xb5\xd0\xbd\xd0\xb5\xd0\xb2\xd1\x81\xd0\xba\xd0\xb0\xd1\x8f', 'metro_select', '37.554151 55.601442'], 
[91, '95', '\xd0\x9d\xd0\xbe\xd0\xb2\xd1\x8b\xd0\xb5 \xd1\x87\xd0\xb5\xd1\x80\xd0\xb5\xd0\xbc\xd1\x83\xd1\x88\xd0\xba\xd0\xb8', 'metro_select', '37.554493 55.670316'], 
[92, '100', '\xd0\x9e\xd0\xba\xd1\x82\xd1\x8f\xd0\xb1\xd1\x80\xd1\x8c\xd1\x81\xd0\xba\xd0\xb0\xd1\x8f', 'metro_select', '37.611221 55.729255'], 
[93, '67', '\xd0\x9e\xd0\xba\xd1\x82\xd1\x8f\xd0\xb1\xd1\x80\xd1\x8c\xd1\x81\xd0\xba\xd0\xbe\xd0\xb5 \xd0\xbf\xd0\xbe\xd0\xbb\xd0\xb5', 'metro_select', '37.493605 55.793505'], 
[94, '20', '\xd0\x9e\xd1\x80\xd0\xb5\xd1\x85\xd0\xbe\xd0\xb2\xd0\xbe', 'metro_select', '37.695681 55.613499'], 
[95, '111', '\xd0\x9e\xd1\x82\xd1\x80\xd0\xb0\xd0\xb4\xd0\xbd\xd0\xbe\xd0\xb5', 'metro_select', '37.604843 55.863384'], 
[96, '31', '\xd0\x9e\xd1\x85\xd0\xbe\xd1\x82\xd0\xbd\xd1\x8b\xd0\xb9 \xd0\xa0\xd1\x8f\xd0\xb4', 'metro_select', '37.617312 55.757247'], 
[97, '12', '\xd0\x9f\xd0\xb0\xd0\xb2\xd0\xb5\xd0\xbb\xd0\xb5\xd1\x86\xd0\xba\xd0\xb0\xd1\x8f', 'metro_select', '37.637335 55.731607'], 
[98, '28', '\xd0\x9f\xd0\xb0\xd1\x80\xd0\xba \xd0\x9a\xd1\x83\xd0\xbb\xd1\x8c\xd1\x82\xd1\x83\xd1\x80\xd1\x8b', 'metro_select', '37.593659 55.735373'], 
[99, '165', '\xd0\x9f\xd0\xb0\xd1\x80\xd0\xba \xd0\x9f\xd0\xbe\xd0\xb1\xd0\xb5\xd0\xb4\xd1\x8b', 'metro_select', '37.514679 55.736437'], 
[100, '44', '\xd0\x9f\xd0\xb0\xd1\x80\xd1\x82\xd0\xb8\xd0\xb7\xd0\xb0\xd0\xbd\xd1\x81\xd0\xba\xd0\xb0\xd1\x8f', 'metro_select', '37.748681 55.787573'], 
[101, '42', '\xd0\x9f\xd0\xb5\xd1\x80\xd0\xb2\xd0\xbe\xd0\xbc\xd0\xb0\xd0\xb9\xd1\x81\xd0\xba\xd0\xb0\xd1\x8f', 'metro_select', '37.799355 55.794553'], 
[102, '83', '\xd0\x9f\xd0\xb5\xd1\x80\xd0\xbe\xd0\xb2\xd0\xbe', 'metro_select', '37.786339 55.751173'], 
[103, '113', '\xd0\x9f\xd0\xb5\xd1\x82\xd1\x80\xd0\xbe\xd0\xb2\xd1\x81\xd0\xba\xd0\xbe-\xd0\xa0\xd0\xb0\xd0\xb7\xd1\x83\xd0\xbc\xd0\xbe\xd0\xb2\xd1\x81\xd0\xba\xd0\xb0\xd1\x8f', 'metro_select', '37.574840 55.836039'], 
[104, '141', '\xd0\x9f\xd0\xb5\xd1\x87\xd0\xb0\xd1\x82\xd0\xbd\xd0\xb8\xd0\xba\xd0\xb8', 'metro_select', '37.728101 55.692704'], 
[105, '59', '\xd0\x9f\xd0\xb8\xd0\xbe\xd0\xbd\xd0\xb5\xd1\x80\xd1\x81\xd0\xba\xd0\xb0\xd1\x8f', 'metro_select', '37.467114 55.736027'], 
[106, '63', '\xd0\x9f\xd0\xbb\xd0\xb0\xd0\xbd\xd0\xb5\xd1\x80\xd0\xbd\xd0\xb0\xd1\x8f', 'metro_select', '37.436679 55.860499'], 
[107, '86', '\xd0\x9f\xd0\xbb\xd0\xbe\xd1\x89\xd0\xb0\xd0\xb4\xd1\x8c \xd0\x98\xd0\xbb\xd1\x8c\xd0\xb8\xd1\x87\xd0\xb0', 'metro_select', '37.680868 55.746968'], 
[108, '49', '\xd0\x9f\xd0\xbb\xd0\xbe\xd1\x89\xd0\xb0\xd0\xb4\xd1\x8c \xd1\x80\xd0\xb5\xd0\xb2\xd0\xbe\xd0\xbb\xd1\x8e\xd1\x86\xd0\xb8\xd0\xb8', 'metro_select', '37.622666 55.756918'], 
[109, '68', '\xd0\x9f\xd0\xbe\xd0\xbb\xd0\xb5\xd0\xb6\xd0\xb0\xd0\xb5\xd0\xb2\xd1\x81\xd0\xba\xd0\xb0\xd1\x8f', 'metro_select', '37.519279 55.777535'], 
[110, '121', '\xd0\x9f\xd0\xbe\xd0\xbb\xd1\x8f\xd0\xbd\xd0\xba\xd0\xb0', 'metro_select', '37.619216 55.736802'], 
[111, '130', '\xd0\x9f\xd1\x80\xd0\xb0\xd0\xb6\xd1\x81\xd0\xba\xd0\xb0\xd1\x8f', 'metro_select', '37.603981 55.612238'], 
[112, '38', '\xd0\x9f\xd1\x80\xd0\xb5\xd0\xbe\xd0\xb1\xd1\x80\xd0\xb0\xd0\xb6\xd0\xb5\xd0\xbd\xd1\x81\xd0\xba\xd0\xb0\xd1\x8f \xd0\xbf\xd0\xbb\xd0\xbe\xd1\x89\xd0\xb0\xd0\xb4\xd1\x8c', 'metro_select', '37.715237 55.796157'], 
[113, '76', '\xd0\x9f\xd1\x80\xd0\xbe\xd0\xbb\xd0\xb5\xd1\x82\xd0\xb0\xd1\x80\xd1\x81\xd0\xba\xd0\xb0\xd1\x8f', 'metro_select', '37.667788 55.732017'], 
[114, '136', '\xd0\x9f\xd1\x80\xd0\xbe\xd1\x81\xd0\xbf\xd0\xb5\xd0\xba\xd1\x82 \xd0\x9c\xd0\xb8\xd1\x80\xd0\xb0', 'metro_select', '37.633688 55.779849'], 
[115, '96', '\xd0\x9f\xd1\x80\xd0\xbe\xd1\x84\xd1\x81\xd0\xbe\xd1\x8e\xd0\xb7\xd0\xbd\xd0\xb0\xd1\x8f', 'metro_select', '37.562865 55.677930'], 
[116, '72', '\xd0\x9f\xd1\x83\xd1\x88\xd0\xba\xd0\xb8\xd0\xbd\xd1\x81\xd0\xba\xd0\xb0\xd1\x8f', 'metro_select', '37.606748 55.765068'], 
[117, '214', '\xd0\x9f\xd1\x8f\xd1\x82\xd0\xbd\xd0\xb8\xd1\x86\xd0\xba\xd0\xbe\xd0\xb5 \xd1\x88\xd0\xbe\xd1\x81\xd1\x81\xd0\xb5', 'metro_select', '37.354025 55.855644'], 
[118, '1', '\xd0\xa0\xd0\xb5\xd1\x87\xd0\xbd\xd0\xbe\xd0\xb9 \xd0\xb2\xd0\xbe\xd0\xba\xd0\xb7\xd0\xb0\xd0\xbb', 'metro_select', '37.476231 55.854891'], 
[119, '104', '\xd0\xa0\xd0\xb8\xd0\xb6\xd1\x81\xd0\xba\xd0\xb0\xd1\x8f', 'metro_select', '37.636563 55.792412'], 
[120, '138', '\xd0\xa0\xd0\xb8\xd0\xbc\xd1\x81\xd0\xba\xd0\xb0\xd1\x8f', 'metro_select', '37.680032 55.746360'], 
[121, '80', '\xd0\xa0\xd1\x8f\xd0\xb7\xd0\xb0\xd0\xbd\xd1\x81\xd0\xba\xd0\xb8\xd0\xb9 \xd0\xbf\xd1\x80\xd0\xbe\xd1\x81\xd0\xbf\xd0\xb5\xd0\xba\xd1\x82', 'metro_select', '37.793130 55.716869'], 
[122, '116', '\xd0\xa1\xd0\xb0\xd0\xb2\xd0\xb5\xd0\xbb\xd0\xbe\xd0\xb2\xd1\x81\xd0\xba\xd0\xb0\xd1\x8f', 'metro_select', '37.588359 55.793520'], 
[123, '108', '\xd0\xa1\xd0\xb2\xd0\xb8\xd0\xb1\xd0\xbb\xd0\xbe\xd0\xb2\xd0\xbe', 'metro_select', '37.652705 55.855416'], 
[124, '127', '\xd0\xa1\xd0\xb5\xd0\xb2\xd0\xb0\xd1\x81\xd1\x82\xd0\xbe\xd0\xbf\xd0\xbe\xd0\xbb\xd1\x8c\xd1\x81\xd0\xba\xd0\xb0\xd1\x8f', 'metro_select', '37.598474 55.651430'], 
[125, '45', '\xd0\xa1\xd0\xb5\xd0\xbc\xd0\xb5\xd0\xbd\xd0\xbe\xd0\xb2\xd1\x81\xd0\xba\xd0\xb0\xd1\x8f', 'metro_select', '37.719693 55.783271'], 
[126, '122', '\xd0\xa1\xd0\xb5\xd1\x80\xd0\xbf\xd1\x83\xd1\x85\xd0\xbe\xd0\xb2\xd1\x81\xd0\xba\xd0\xb0\xd1\x8f', 'metro_select', '37.624211 55.726928'], 
[127, '192', '\xd0\xa1\xd0\xba\xd0\xbe\xd0\xb1\xd0\xb5\xd0\xbb\xd0\xb5\xd0\xb2\xd1\x81\xd0\xba\xd0\xb0\xd1\x8f \xd1\x83\xd0\xbb\xd0\xb8\xd1\x86\xd0\xb0', 'metro_select', '37.554699 55.548243'], 
[128, '201', '\xd0\xa1\xd0\xbb\xd0\xb0\xd0\xb2\xd1\x8f\xd0\xbd\xd1\x81\xd0\xba\xd0\xb8\xd0\xb9 \xd0\xb1\xd1\x83\xd0\xbb\xd1\x8c\xd0\xb2\xd0\xb0\xd1\x80', 'metro_select', '37.471102 55.729518'], 
[129, '51', '\xd0\xa1\xd0\xbc\xd0\xbe\xd0\xbb\xd0\xb5\xd0\xbd\xd1\x81\xd0\xba\xd0\xb0\xd1\x8f', 'metro_select', '37.582403 55.749395'], 
[130, '4', '\xd0\xa1\xd0\xbe\xd0\xba\xd0\xbe\xd0\xbb', 'metro_select', '37.514976 55.804992'], 
[131, '37', '\xd0\xa1\xd0\xbe\xd0\xba\xd0\xbe\xd0\xbb\xd1\x8c\xd0\xbd\xd0\xb8\xd0\xba\xd0\xb8', 'metro_select', '37.679709 55.789259'], 
[132, '26', '\xd0\xa1\xd0\xbf\xd0\xbe\xd1\x80\xd1\x82\xd0\xb8\xd0\xb2\xd0\xbd\xd0\xb0\xd1\x8f', 'metro_select', '37.563961 55.723110'], 
[133, '206', '\xd0\xa1\xd1\x80\xd0\xb5\xd1\x82\xd0\xb5\xd0\xbd\xd1\x81\xd0\xba\xd0\xb8\xd0\xb9 \xd0\xb1\xd1\x83\xd0\xbb\xd1\x8c\xd0\xb2\xd0\xb0\xd1\x80', 'metro_select', '37.635817 55.765949'], 
[134, '212', '\xd0\xa1\xd1\x82\xd0\xb0\xd1\x80\xd0\xbe\xd0\xba\xd0\xb0\xd1\x87\xd0\xb0\xd0\xbb\xd0\xbe\xd0\xb2\xd1\x81\xd0\xba\xd0\xb0\xd1\x8f', 'metro_select', '37.576708 55.568838'], 
[135, '200', '\xd0\xa1\xd1\x82\xd1\x80\xd0\xbe\xd0\xb3\xd0\xb8\xd0\xbd\xd0\xbe', 'metro_select', '37.402534 55.803783'], 
[136, '54', '\xd0\xa1\xd1\x82\xd1\x83\xd0\xb4\xd0\xb5\xd0\xbd\xd1\x87\xd0\xb5\xd1\x81\xd0\xba\xd0\xb0\xd1\x8f', 'metro_select', '37.548483 55.738688'], 
[137, '102', '\xd0\xa1\xd1\x83\xd1\x85\xd0\xb0\xd1\x80\xd0\xb5\xd0\xb2\xd1\x81\xd0\xba\xd0\xb0\xd1\x8f', 'metro_select', '37.632790 55.772958'], 
[138, '64', '\xd0\xa1\xd1\x85\xd0\xbe\xd0\xb4\xd0\xbd\xd0\xb5\xd0\xbd\xd1\x81\xd0\xba\xd0\xb0\xd1\x8f', 'metro_select', '37.439805 55.850429'], 
[139, '75', '\xd0\xa2\xd0\xb0\xd0\xb3\xd0\xb0\xd0\xbd\xd1\x81\xd0\xba\xd0\xb0\xd1\x8f', 'metro_select', '37.653433 55.742372'], 
[140, '9', '\xd0\xa2\xd0\xb2\xd0\xb5\xd1\x80\xd1\x81\xd0\xba\xd0\xb0\xd1\x8f', 'metro_select', '37.605221 55.766263'], 
[141, '10', '\xd0\xa2\xd0\xb5\xd0\xb0\xd1\x82\xd1\x80\xd0\xb0\xd0\xbb\xd1\x8c\xd0\xbd\xd0\xb0\xd1\x8f', 'metro_select', '37.618830 55.757409'], 
[142, '78', '\xd0\xa2\xd0\xb5\xd0\xba\xd1\x81\xd1\x82\xd0\xb8\xd0\xbb\xd1\x8c\xd1\x89\xd0\xb8\xd0\xba\xd0\xb8', 'metro_select', '37.731335 55.709221'], 
[143, '91', '\xd0\xa2\xd0\xb5\xd0\xbf\xd0\xbb\xd1\x8b\xd0\xb9 \xd1\x81\xd1\x82\xd0\xb0\xd0\xbd', 'metro_select', '37.507511 55.618827'], 
[144, '114', '\xd0\xa2\xd0\xb8\xd0\xbc\xd0\xb8\xd1\x80\xd1\x8f\xd0\xb7\xd0\xb5\xd0\xb2\xd1\x81\xd0\xba\xd0\xb0\xd1\x8f', 'metro_select', '37.576007 55.818407'], 
[145, '88', '\xd0\xa2\xd1\x80\xd0\xb5\xd1\x82\xd1\x8c\xd1\x8f\xd0\xba\xd0\xbe\xd0\xb2\xd1\x81\xd0\xba\xd0\xb0\xd1\x8f', 'metro_select', '37.629188 55.741120'], 
[146, '199', '\xd0\xa2\xd1\x80\xd1\x83\xd0\xb1\xd0\xbd\xd0\xb0\xd1\x8f', 'metro_select', '37.622055 55.767468'], 
[147, '123', '\xd0\xa2\xd1\x83\xd0\xbb\xd1\x8c\xd1\x81\xd0\xba\xd0\xb0\xd1\x8f', 'metro_select', '37.622675 55.708739'], 
[148, '103', '\xd0\xa2\xd1\x83\xd1\x80\xd0\xb3\xd0\xb5\xd0\xbd\xd0\xb5\xd0\xb2\xd1\x81\xd0\xba\xd0\xb0\xd1\x8f', 'metro_select', '37.637380 55.765716'], 
[149, '65', '\xd0\xa2\xd1\x83\xd1\x88\xd0\xb8\xd0\xbd\xd1\x81\xd0\xba\xd0\xb0\xd1\x8f', 'metro_select', '37.436894 55.826316'], 
[150, '70', '\xd0\xa3\xd0\xbb\xd0\xb8\xd1\x86\xd0\xb0 1905 \xd0\xb3\xd0\xbe\xd0\xb4\xd0\xb0', 'metro_select', '37.561571 55.765053'], 
[151, '194', '\xd0\xa3\xd0\xbb\xd0\xb8\xd1\x86\xd0\xb0 \xd0\x93\xd0\xbe\xd1\x80\xd1\x87\xd0\xb0\xd0\xba\xd0\xbe\xd0\xb2\xd0\xb0', 'metro_select', '37.531235 55.541830'], 
[152, '40', '\xd0\xa3\xd0\xbb\xd0\xb8\xd1\x86\xd0\xb0 \xd0\x9f\xd0\xbe\xd0\xb4\xd0\xb1\xd0\xb5\xd0\xbb\xd1\x8c\xd1\x81\xd0\xba\xd0\xbe\xd0\xb3\xd0\xbe', 'metro_select', '37.733742 55.814533'], 
[153, '211', '\xd1\x83\xd0\xbb\xd0\xb8\xd1\x86\xd0\xb0 \xd0\xa1\xd0\xb5\xd1\x80\xd0\xb3\xd0\xb5\xd1\x8f \xd0\xad\xd0\xb9\xd0\xb7\xd0\xb5\xd0\xbd\xd1\x88\xd1\x82\xd0\xb5\xd0\xb9\xd0\xbd\xd0\xb0', 'metro_select', '37.644998 55.829305'], 
[154, '25', '\xd0\xa3\xd0\xbd\xd0\xb8\xd0\xb2\xd0\xb5\xd1\x80\xd1\x81\xd0\xb8\xd1\x82\xd0\xb5\xd1\x82', 'metro_select', '37.534667 55.692592'], 
[155, '193', '\xd0\xa3\xd1\x88\xd0\xb0\xd0\xba\xd0\xbe\xd0\xb2\xd0\xb0 \xd0\xb0\xd0\xb4\xd0\xbc\xd0\xb8\xd1\x80\xd0\xb0\xd0\xbb\xd0\xb0 \xd0\xb1\xd1\x83\xd0\xbb\xd1\x8c\xd0\xb2\xd0\xb0\xd1\x80', 'metro_select', '37.543048 55.545416'], 
[156, '58', '\xd0\xa4\xd0\xb8\xd0\xbb\xd0\xb5\xd0\xb2\xd1\x81\xd0\xba\xd0\xb8\xd0\xb9 \xd0\xbf\xd0\xb0\xd1\x80\xd0\xba', 'metro_select', '37.483328 55.739549'], 
[157, '56', '\xd0\xa4\xd0\xb8\xd0\xbb\xd0\xb8', 'metro_select', '37.514823 55.746142'], 
[158, '27', '\xd0\xa4\xd1\x80\xd1\x83\xd0\xbd\xd0\xb7\xd0\xb5\xd0\xbd\xd1\x81\xd0\xba\xd0\xb0\xd1\x8f', 'metro_select', '37.580220 55.727607'], 
[159, '19', '\xd0\xa6\xd0\xb0\xd1\x80\xd0\xb8\xd1\x86\xd1\x8b\xd0\xbd\xd0\xbe', 'metro_select', '37.670142 55.621658'], 
[160, '118', '\xd0\xa6\xd0\xb2\xd0\xb5\xd1\x82\xd0\xbd\xd0\xbe\xd0\xb9 \xd0\xb1\xd1\x83\xd0\xbb\xd1\x8c\xd0\xb2\xd0\xb0\xd1\x80', 'metro_select', '37.621255 55.772087'], 
[161, '39', '\xd0\xa7\xd0\xb5\xd1\x80\xd0\xba\xd0\xb8\xd0\xb7\xd0\xbe\xd0\xb2\xd1\x81\xd0\xba\xd0\xb0\xd1\x8f', 'metro_select', '37.746714 55.803272'], 
[162, '128', '\xd0\xa7\xd0\xb5\xd1\x80\xd1\x82\xd0\xb0\xd0\xbd\xd0\xbe\xd0\xb2\xd1\x81\xd0\xba\xd0\xb0\xd1\x8f', 'metro_select', '37.605939 55.641468'], 
[163, '119', '\xd0\xa7\xd0\xb5\xd1\x85\xd0\xbe\xd0\xb2\xd1\x81\xd0\xba\xd0\xb0\xd1\x8f', 'metro_select', '37.607520 55.765807'], 
[164, '33', '\xd0\xa7\xd0\xb8\xd1\x81\xd1\x82\xd1\x8b\xd0\xb5 \xd0\xbf\xd1\x80\xd1\x83\xd0\xb4\xd1\x8b', 'metro_select', '37.638476 55.765281'], 
[165, '137', '\xd0\xa7\xd0\xba\xd0\xb0\xd0\xbb\xd0\xbe\xd0\xb2\xd1\x81\xd0\xba\xd0\xb0\xd1\x8f', 'metro_select', '37.659164 55.756822'], 
[166, '99', '\xd0\xa8\xd0\xb0\xd0\xb1\xd0\xbe\xd0\xbb\xd0\xbe\xd0\xb2\xd1\x81\xd0\xba\xd0\xb0\xd1\x8f', 'metro_select', '37.608257 55.719176'], 
[167, '208', '\xd0\xa8\xd0\xb8\xd0\xbf\xd0\xb8\xd0\xbb\xd0\xbe\xd0\xb2\xd1\x81\xd0\xba\xd0\xb0\xd1\x8f', 'metro_select', '37.743027 55.621949'], 
[168, '84', '\xd0\xa8\xd0\xbe\xd1\x81\xd1\x81\xd0\xb5 \xd1\x8d\xd0\xbd\xd1\x82\xd1\x83\xd0\xb7\xd0\xb8\xd0\xb0\xd1\x81\xd1\x82\xd0\xbe\xd0\xb2', 'metro_select', '37.752149 55.758899'], 
[169, '41', '\xd0\xa9\xd0\xb5\xd0\xbb\xd0\xba\xd0\xbe\xd0\xb2\xd1\x81\xd0\xba\xd0\xb0\xd1\x8f', 'metro_select', '37.798538 55.810921'], 
[170, '66', '\xd0\xa9\xd1\x83\xd0\xba\xd0\xb8\xd0\xbd\xd1\x81\xd0\xba\xd0\xb0\xd1\x8f', 'metro_select', '37.464212 55.808548'], 
[171, '46', '\xd0\xad\xd0\xbb\xd0\xb5\xd0\xba\xd1\x82\xd1\x80\xd0\xbe\xd0\xb7\xd0\xb0\xd0\xb2\xd0\xbe\xd0\xb4\xd1\x81\xd0\xba\xd0\xb0\xd1\x8f', 'metro_select', '37.706685 55.782218'], 
[172, '23', '\xd0\xae\xd0\xb3\xd0\xbe-\xd0\x97\xd0\xb0\xd0\xbf\xd0\xb0\xd0\xb4\xd0\xbd\xd0\xb0\xd1\x8f', 'metro_select', '37.483319 55.663771'], 
[173, '129', '\xd0\xae\xd0\xb6\xd0\xbd\xd0\xb0\xd1\x8f', 'metro_select', '37.608670 55.622360'], 
[174, '155', '\xd0\xaf\xd0\xbd\xd0\xb3\xd0\xb5\xd0\xbb\xd1\x8f \xd0\x90\xd0\xba\xd0\xb0\xd0\xb4\xd0\xb5\xd0\xbc\xd0\xb8\xd0\xba\xd0\xb0', 'metro_select', '37.600819 55.595521'], 
[175, '90', '\xd0\xaf\xd1\x81\xd0\xb5\xd0\xbd\xd0\xb5\xd0\xb2\xd0\xbe', 'metro_select', '37.533301 55.606085']]


'''[[1,'85','Авиамоторная','metro_select','37.717052 55.751558'],
                [2,'13','Автозаводская','metro_select','37.657440 55.707167'],
                [3,'97','Академическая','metro_select','37.573555 55.687868'],
                [4,'53','Александровский сад','metro_select','37.610009 55.752298'],
                [5,'105','Алексеевская','metro_select','37.638979 55.808295'],
                [6,'213','Алма-Атинская','metro_select','37.765678 55.63349'],
                [7,'135','Алтуфьево','metro_select','37.587128 55.897912'],
                [8,'156','Аннино','metro_select','37.596830 55.583250'],
                [9,'50','Арбатская','metro_select','37.601753 55.752404'],
                [10,'5','Аэропорт','metro_select','37.533706 55.800812'],
                [11,'109','Бабушкинская','metro_select','37.664150 55.869602'],
                [12,'57','Багратионовская','metro_select','37.497710 55.743735'],
                [13,'71','Баррикадная','metro_select','37.581280 55.760803'],
                [14,'47','Бауманская','metro_select','37.679520 55.772472'],
                [15,'69','Беговая','metro_select','37.546821 55.773682'],
                [16,'7','Белорусская','metro_select','37.582242 55.775717'],
                [17,'93','Беляево','metro_select','37.526304 55.642464'],
                [18,'131','Бибирево','metro_select','37.602687 55.884272'],
                [19,'30','Библиотека Ленина','metro_select','37.610997 55.752698'],
                [20,'207','Борисово','metro_select','37.742598 55.635400'],
                [21,'120','Боровицкая','metro_select','37.610152 55.751705'],
                [22,'107','Ботанический сад','metro_select','37.638225 55.845451'],
                [23,'145','Братиславская','metro_select','37.750801 55.659500'],
                [24,'195','Бунинская аллея','metro_select','37.516781 55.537974'],
                [25,'106','ВДНХ','metro_select','37.641315 55.821032'],
                [26,'16','Варшавская','metro_select','37.619558 55.653492'],
                [27,'24','Вернадского проспект','metro_select','37.506091 55.676945'],
                [28,'112','Владыкино','metro_select','37.589877 55.847280'],
                [29,'2','Водный стадион','metro_select','37.487128 55.839840'],
                [30,'3','Войковская','metro_select','37.497791 55.818923'],
                [31,'77','Волгоградский проспект','metro_select','37.686527 55.725275'],
                [32,'142','Волжская','metro_select','37.752823 55.690755'],
                [33,'203','Волоколамская','metro_select','37.381810 55.835594'],
                [34,'157','Воробьевы горы','metro_select','37.559137 55.710246'],
                [35,'198','Выставочная','metro_select','37.542770 55.750195'],
                [36,'81','Выхино','metro_select','37.817807 55.715961'],
                [37,'6','Динамо','metro_select','37.558230 55.789821'],
                [38,'115','Дмитровская','metro_select','37.581200 55.807547'],
                [39,'132','Добрынинская','metro_select','37.622594 55.729057'],
                [40,'21','Домодедовская','metro_select','37.719594 55.610956'],
                [41,'164','Донского Дмитрия бульвар','metro_select','37.576367 55.569382'],
                [42,'205','Достоевская','metro_select','37.613737 55.781742'],
                [43,'140','Дубровка','metro_select','37.677212 55.717274'],
                [44,'216','Жулебино','metro_select','37.855123 55.684539'],
                [45,'209','Зябликово','metro_select','37.744529 55.612307'],
                [46,'43','Измайловская','metro_select','37.781380 55.787680'],
                [47,'94','Калужская','metro_select','37.540488 55.657134'],
                [48,'18','Кантемировская','metro_select','37.656613 55.635782'],
                [49,'17','Каховская','metro_select','37.598286 55.652994'],
                [50,'15','Каширская','metro_select','37.648690 55.655239'],
                [51,'52','Киевская','metro_select','37.567312 55.744678'],
                [52,'74','Китай-город','metro_select','37.633823 55.755398'],
                [53,'144','Кожуховская','metro_select','37.685593 55.706203'],
                [54,'14','Коломенская','metro_select','37.663889 55.678387'],
                [55,'35','Комсомольская','metro_select','37.656029 55.774659'],
                [56,'92','Коньково','metro_select','37.519360 55.633109'],
                [57,'22','Красногвардейская','metro_select','37.744522 55.614048'],
                [58,'133','Краснопресненская','metro_select','37.577543 55.760596'],
                [59,'36','Красносельская','metro_select','37.666279 55.780117'],
                [60,'34','Красные ворота','metro_select','37.649094 55.768876'],
                [61,'139','Крестьянская застава','metro_select','37.665722 55.732448'],
                [62,'29','Кропоткинская','metro_select','37.602777 55.745144'],
                [63,'62','Крылатское','metro_select','37.408130 55.756862'],
                [64,'73','Кузнецкий мост','metro_select','37.624903 55.761259'],
                [65,'79','Кузьминки','metro_select','37.765417 55.705452'],
                [66,'60','Кунцевская','metro_select','37.446003 55.730791'],
                [67,'48','Курская','metro_select','37.659928 55.758179'],
                [68,'55','Кутузовская','metro_select','37.534173 55.739965'],
                [69,'98','Ленинский проспект','metro_select','37.586158 55.707491'],
                [70,'215','Лермонтовский проспект','metro_select','37.852275 55.701765'],
                [71,'32','Лубянка','metro_select','37.625873 55.760150'],
                [72,'143','Люблино','metro_select','37.761473 55.675753'],
                [73,'87','Марксистская','metro_select','37.656577 55.741140'],
                [74,'204','Марьина роща','metro_select','37.61662 55.795449'],
                [75,'146','Марьино','metro_select','37.743902 55.650150'],
                [76,'8','Маяковская','metro_select','37.597001 55.769433'],
                [77,'110','Медведково','metro_select','37.661563 55.887215'],
                [78,'197','Международная','metro_select','37.533454 55.748300'],
                [79,'117','Менделеевская','metro_select','37.599759 55.781529'],
                [80,'196','Митино','metro_select','37.354923 55.846113'],
                [81,'61','Молодежная','metro_select','37.417050 55.740912'],
                [82,'202','Мякинино','metro_select','37.384738 55.82399'],
                [83,'124','Нагатинская','metro_select','37.622127 55.683163'],
                [84,'125','Нагорная','metro_select','37.611122 55.673225'],
                [85,'126','Нахимовский проспект','metro_select','37.605292 55.662654'],
                [86,'82','Новогиреево','metro_select','37.816675 55.751867'],
                [87,'210','Новокосино','metro_select','37.864149 55.744844'],
                [88,'11','Новокузнецкая','metro_select','37.629592 55.742134'],
                [89,'134','Новослободская','metro_select','37.601501 55.779707'],
                [90,'89','Новоясеневская','metro_select','37.554151 55.601442'],
                [91,'95','Новые черемушки','metro_select','37.554493 55.670316'],
                [92,'100','Октябрьская','metro_select','37.611221 55.729255'],
                [93,'67','Октябрьское поле','metro_select','37.493605 55.793505'],
                [94,'20','Орехово','metro_select','37.695681 55.613499'],
                [95,'111','Отрадное','metro_select','37.604843 55.863384'],
                [96,'31','Охотный Ряд','metro_select','37.617312 55.757247'],
                [97,'12','Павелецкая','metro_select','37.637335 55.731607'],
                [98,'28','Парк Культуры','metro_select','37.593659 55.735373'],
                [99,'165','Парк Победы','metro_select','37.514679 55.736437'],[100,'44','Партизанская','metro_select','37.748681 55.787573'],[101,'42','Первомайская','metro_select','37.799355 55.794553'],[102,'83','Перово','metro_select','37.786339 55.751173'],[103,'113','Петровско-Разумовская','metro_select','37.574840 55.836039'],[104,'141','Печатники','metro_select','37.728101 55.692704'],[105,'59','Пионерская','metro_select','37.467114 55.736027'],[106,'63','Планерная','metro_select','37.436679 55.860499'],[107,'86','Площадь Ильича','metro_select','37.680868 55.746968'],[108,'49','Площадь революции','metro_select','37.622666 55.756918'],[109,'68','Полежаевская','metro_select','37.519279 55.777535'],[110,'121','Полянка','metro_select','37.619216 55.736802'],[111,'130','Пражская','metro_select','37.603981 55.612238'],[112,'38','Преображенская площадь','metro_select','37.715237 55.796157'],[113,'76','Пролетарская','metro_select','37.667788 55.732017'],[114,'136','Проспект Мира','metro_select','37.633688 55.779849'],[115,'96','Профсоюзная','metro_select','37.562865 55.677930'],[116,'72','Пушкинская','metro_select','37.606748 55.765068'],[117,'214','Пятницкое шоссе','metro_select','37.354025 55.855644'],[118,'1','Речной вокзал','metro_select','37.476231 55.854891'],[119,'104','Рижская','metro_select','37.636563 55.792412'],[120,'138','Римская','metro_select','37.680032 55.746360'],[121,'80','Рязанский проспект','metro_select','37.793130 55.716869'],[122,'116','Савеловская','metro_select','37.588359 55.793520'],[123,'108','Свиблово','metro_select','37.652705 55.855416'],[124,'127','Севастопольская','metro_select','37.598474 55.651430'],[125,'45','Семеновская','metro_select','37.719693 55.783271'],[126,'122','Серпуховская','metro_select','37.624211 55.726928'],[127,'192','Скобелевская улица','metro_select','37.554699 55.548243'],[128,'201','Славянский бульвар','metro_select','37.471102 55.729518'],[129,'51','Смоленская','metro_select','37.582403 55.749395'],[130,'4','Сокол','metro_select','37.514976 55.804992'],[131,'37','Сокольники','metro_select','37.679709 55.789259'],[132,'26','Спортивная','metro_select','37.563961 55.723110'],[133,'206','Сретенский бульвар','metro_select','37.635817 55.765949'],[134,'212','Старокачаловская','metro_select','37.576708 55.568838'],[135,'200','Строгино','metro_select','37.402534 55.803783'],[136,'54','Студенческая','metro_select','37.548483 55.738688'],[137,'102','Сухаревская','metro_select','37.632790 55.772958'],[138,'64','Сходненская','metro_select','37.439805 55.850429'],[139,'75','Таганская','metro_select','37.653433 55.742372'],[140,'9','Тверская','metro_select','37.605221 55.766263'],[141,'10','Театральная','metro_select','37.618830 55.757409'],[142,'78','Текстильщики','metro_select','37.731335 55.709221'],[143,'91','Теплый стан','metro_select','37.507511 55.618827'],[144,'114','Тимирязевская','metro_select','37.576007 55.818407'],[145,'88','Третьяковская','metro_select','37.629188 55.741120'],[146,'199','Трубная','metro_select','37.622055 55.767468'],[147,'123','Тульская','metro_select','37.622675 55.708739'],[148,'103','Тургеневская','metro_select','37.637380 55.765716'],[149,'65','Тушинская','metro_select','37.436894 55.826316'],[150,'70','Улица 1905 года','metro_select','37.561571 55.765053'],[151,'194','Улица Горчакова','metro_select','37.531235 55.541830'],[152,'40','Улица Подбельского','metro_select','37.733742 55.814533'],[153,'211','улица Сергея Эйзенштейна','metro_select','37.644998 55.829305'],[154,'25','Университет','metro_select','37.534667 55.692592'],[155,'193','Ушакова адмирала бульвар','metro_select','37.543048 55.545416'],[156,'58','Филевский парк','metro_select','37.483328 55.739549'],[157,'56','Фили','metro_select','37.514823 55.746142'],[158,'27','Фрунзенская','metro_select','37.580220 55.727607'],[159,'19','Царицыно','metro_select','37.670142 55.621658'],[160,'118','Цветной бульвар','metro_select','37.621255 55.772087'],[161,'39','Черкизовская','metro_select','37.746714 55.803272'],[162,'128','Чертановская','metro_select','37.605939 55.641468'],[163,'119','Чеховская','metro_select','37.607520 55.765807'],[164,'33','Чистые пруды','metro_select','37.638476 55.765281'],[165,'137','Чкаловская','metro_select','37.659164 55.756822'],[166,'99','Шаболовская','metro_select','37.608257 55.719176'],[167,'208','Шипиловская','metro_select','37.743027 55.621949'],[168,'84','Шоссе энтузиастов','metro_select','37.752149 55.758899'],[169,'41','Щелковская','metro_select','37.798538 55.810921'],[170,'66','Щукинская','metro_select','37.464212 55.808548'],[171,'46','Электрозаводская','metro_select','37.706685 55.782218'],[172,'23','Юго-Западная','metro_select','37.483319 55.663771'],[173,'129','Южная','metro_select','37.608670 55.622360'],[174,'155','Янгеля Академика','metro_select','37.600819 55.595521'],
                [175,'90','Ясенево','metro_select','37.533301 55.606085']]'''



names = u'''Авдотья\n
Аким\n
Аксинья\n
Алевтина\n
Александр\n
Александра\n
Алексей\n
Алена\n
Алина\n
Алла\n
Анастасия\n
Анатолий\n
Ангелина\n
Андрей\n
Анисья\n
Анна\n
Аня\n
Антон\n
Антонина\n
Анфим\n
Анфиса\n
Аполлинария\n
Арина\n
Аркадий\n
Арсений\n
Артем\n
Артемий\n
Богдан\n
Богдана\n
Борис\n
Борислав\n
Вадим\n
Валентин\n
Валентина\n
Валерий\n
Валерия\n
Варвара\n
Василий\n
Василиса\n
Венера\n
Вера\n
Вета\n
Виктор\n
Викторина\n
Виктория\n
Вилена\n
Виолетта\n
Виталий\n
Виталина\n
Виталия\n
Влада\n
Владана\n
Владимир\n
Владислав\n
Владислава\n
Владлен\n
Всеволод\n
Вячеслав\n
Галина\n
Геннадий\n
Георгий\n
Герасим\n
Глеб\n
Гордей\n
Григорий\n
Дамир\n
Даниил\n
Данислав\n
Дарья\n
Денис\n
Джереми\n
Иеремия\n
Дина\n
Дмитрий\n
Дима\n
Евгений\n
Женя\n
Евгения\n
Евдоким\n
Евдокия\n
Евстахий\n
Егор\n
Екатерина\n
Катя\n
Елена\n
Лена\n
Елизавета\n
Лиза\n
Елисей\n
Емельян\n
Еремей\n
Есения\n
Ефим\n
Захар\n
Зинаида\n
Зина\n
Зиновий\n
Злата\n
Зоя\n
Иван\n
Игнат\n
Игнатий\n
Игорь\n
Иероним\n
Джером\n
Изабелла\n
Иллирика\n
Илья\n
Инесса\n
Инна\n
Иннокентий\n
Иоанна\n
Ира\n
Ираида\n
Ирина\n
Искра\n
Ия\n
Карина\n
Кира\n
Кирилл\n
Клим\n
Константин\n
Костя\n
Кристина\n
Ксения\n
Кузьма\n
Лада\n
Лара\n
Лариса\n
Лев\n
Леонид\n
Лера\n
Лидия\n
Лида\n
Лика\n
Лилия\n
Любовь\n
Люба\n
Людмила\n
Люда\n
Ляля\n
Магдалeна\n
Майя\n
Макар\n
Макарий\n
Макария\n
Максим\n
Маргарита\n
Рита\n
Марина\n
Мария\n
Маша\n
Марк\n
Мартин\n
Мартын\n
Марфа\n
Матвей\n
Мила\n
Милада\n
Милана\n
Милена\n
Милица\n
Мира\n
Мирослав\n
Мирослава\n
Мирра\n
Михаил\n
Миша\n
Надежда\n
Надя\n
Наталья\n
Наташа\n
Нелли\n
Ника\n
Никита\n
Никодим\n
Никола\n
Николай\n
Коля\n
Нина\n
Нинель\n
Оксана\n
Олег\n
Олеся\n
Ольга\n
Оля\n
Осип\n
Иосиф\n
Остап\n
Павел\n
Паша\n
Павлина\n
Пелагея\n
Петр\n
Петя\n
Полина\n
Потап\n
Прасковья\n
Прохор\n
Рада\n
Радий\n
Радик\n
Радомир\n
Радослав\n
Раиса\n
Рената\n
Римма\n
Ринат\n
Ренат\n
Родион\n
Роман\n
Рома\n
Ростислав\n
Русалина\n
Руслан\n
Сабина\n
Савва\n
Савелий\n
Светлана\n
Света\n
Святослав\n
Севастьян\n
Семен\n
Серафима\n
Сергей\n
Сидор\n
Соня\n
Софья\n
Спартак\n
Станислав\n
Стас\n
Стелла\n
Степан\n
Таисия\n
Тарас\n
Татьяна\n
Тимофей\n
Тихон\n
Трофим\n
Ульяна\n
Фаина\n
Федор\n
Федя\n
Федот\n
Филипп\n
Флор\n
Фома\n
Харитон\n
Цветана\n
Юлиан\n
Юлия\n
Юния\n
Юрий\n
Яков\n
Яна\n
Янина\n
Ярина\n
Ярослав\n
Ярослава\n'''

names = names.split("\n")
buff_names = names
names = []
for name in buff_names:
    if name != "":
        names.append(name)