__author__ = 'wilrona'

from flask import request, render_template, flash, url_for, redirect, session, make_response, Response
from google.appengine.runtime.apiproxy_errors import CapabilityDisabledError

from lib.flask_cache import Cache
from application import app
from ..decorators import login_required
from flask.ext.login import current_user
from ..decorators import roles_required, login_required

import hashlib
import calendar
import datetime


from google.appengine.api import urlfetch
import json

#import pour l'impression des ticket
from lib.reportlab.pdfgen import canvas
from lib.reportlab.lib.pagesizes import A5
from lib.reportlab.platypus.doctemplate import SimpleDocTemplate
from lib.reportlab.lib.units import cm

#ajoute des fonts dans mes pdfs
import os
import lib.reportlab

from lib.reportlab.platypus import Paragraph
from lib.reportlab.lib.styles import getSampleStyleSheet
from lib.reportlab.pdfbase import pdfmetrics
from lib.reportlab.pdfbase.ttfonts import TTFont
from lib.reportlab.lib.colors import black,white

from lib.reportlab.graphics.barcode import code39, createBarcodeDrawing

# Appel de l'ensemble des fonctions crees
from application import function

# variable pour la gestion automatique des dates en fonction des zones
from lib.pytz.gae import pytz


global_role = {
    'admin': False,
    'manager_agency': False,
    'employee_POS': True,
    'employee_Boarding': True
}

global_agencytype = {
        1: 'Internal',
        2: 'Partnership agency',
        3: 'Coorporate'
}

global_nationality_contry = {
    'abkhazia' : 'Abkhazian',
    'afghanistan' : 'Afghan',
    'albania' : 'Albanian',
    'algeria' : 'Algerian',
    'american samoa' : 'American Samoan',
    'andorra' : 'Andorran',
    'angola' : 'Angolan',
    'anguilla' : 'Anguillan',
    'antigua and barbuda' : 'Antiguan/Barbudan',
    'argentina' : 'Argentinean',
    'armenia' : 'Armenian',
    'aruba' : 'Aruban',
    'australia' : 'Australian',
    'austria' : 'Austrian',
    'azerbaijan' : 'Azerbaijani',
    'bahamas' : 'Bahamian',
    'bahrain' : 'Bahraini',
    'bangladesh' : 'Bangladeshi',
    'barbados' : 'Barbadian',
    'belarus' : 'Belarusian',
    'belgium' : 'Belgian',
    'belize' : 'Belizean',
    'benin' : 'Beninese',
    'bermuda' : 'Bermudian',
    'bhutan' : 'Bhutanese',
    'bolivia' : 'Bolivian',
    'bosnia and herzegovina' : 'Bosnian/Herzegovinian',
    'botswana' : 'Motswana',
    'brazil' : 'Brazilian',
    'british virgin islands' : 'British Virgin Island',
    'brunei' : 'Bruneian',
    'bulgaria' : 'Bulgarian',
    'burkina fasoa' : 'Burkinabe',
    'burmab' : 'Burmese',
    'burundi' : 'Burundian',
    'cambodia' : 'Cambodian',
    'cameroon' : 'Cameroonian',
    'canada' : 'Canadian',
    'cape verde' : 'Cape Verdean',
    'cayman islands' : 'Caymanian',
    'central african republic' : 'Central African',
    'chad' : 'Chadian',
    'chile' : 'Chilean',
    'christmas island' : 'Christmas Island',
    'cocos (keeling) islands' : 'Cocos Island',
    'colombia' : 'Colombian',
    'comoros' : 'Comorian',
    'cook islands' : 'Cook Island',
    'costa rica' : 'Costa Rican',
    'croatia' : 'Croatian',
    'cuba' : 'Cuban',
    'cyprus' : 'Cypriot',
    'czech republic' : 'Czech',
    'cote d\'ivoire' : 'Ivorian',
    'dem. republic of the congo' : 'Congolese',
    'denmark' : 'Danish',
    'djibouti' : 'Djiboutian',
    'dominica' : 'Dominicand',
    'dominican republic' : 'Dominicane',
    'east timor' : 'Timorese',
    'ecuador' : 'Ecuadorian',
    'egypt' : 'Egyptian',
    'el salvador' : 'Salvadoran',
    'england' : 'English',
    'equatorial guinea' : 'Equatorial Guinean',
    'eritrea' : 'Eritrean',
    'estonia' : 'Estonian',
    'ethiopia' : 'Ethiopian',
    'falkland islands' : 'Falkland Island',
    'faroe islands' : 'Faroese',
    'fiji' : 'Fijian',
    'finland' : 'Finnish',
    'france' : 'French',
    'french guiana' : 'French Guianese',
    'french polynesia' : 'French Polynesian',
    'gabon' : 'Gabonese',
    'gambia' : 'Gambian',
    'georgia' : 'Georgian',
    'germany' : 'German',
    'ghana' : 'Ghanaian',
    'gibraltar' : 'Gibraltar',
    'great britain' : 'British',
    'greece' : 'Greek',
    'greenland' : 'Greenlandic',
    'grenada' : 'Grenadian',
    'guadeloupe' : 'Guadeloupe',
    'guam' : 'Guamanian',
    'guatemala' : 'Guatemalan',
    'guinea' : 'Guinean',
    'guinea-bissau' : 'Guinean',
    'guyana' : 'Guyanese',
    'haiti' : 'Haitian',
    'honduras' : 'Honduran',
    'hong kong' : 'Hongkongese',
    'hungary' : 'Hungarian',
    'iceland' : 'Icelandic',
    'india' : 'Indian',
    'indonesia' : 'Indonesian',
    'iran' : 'Iranian',
    'iraq' : 'Iraqi',
    'ireland' : 'Irish',
    'isle of man' : 'Manx',
    'israel' : 'Israeli',
    'italy' : 'Italian',
    'jamaica' : 'Jamaican',
    'japan' : 'Japanese',
    'jordan' : 'Jordanian',
    'kazakhstan' : 'Kazakh',
    'kenya' : 'Kenyan',
    'kiribati' : 'I-Kiribati',
    'kosovo' : 'Kosovar',
    'kuwait' : 'Kuwaiti',
    'kyrgyzstan' : 'Kyrgyzstani',
    'laos' : 'Laotian',
    'latvia' : 'Latvian',
    'lebanon' : 'Lebanese',
    'lesotho' : 'Basotho',
    'liberia' : 'Liberian',
    'libya' : 'Libyan',
    'liechtenstein' : 'Liechtenstein',
    'lithuania' : 'Lithuanian',
    'luxembourg' : 'Luxembourgish',
    'macau' : 'Macanese',
    'madagascar' : 'Malagasy',
    'malawi' : 'Malawian',
    'malaysia' : 'Malaysian',
    'maldives' : 'Maldivian',
    'mali' : 'Malian',
    'malta' : 'Maltese',
    'marshall islands' : 'Marshallese',
    'martinique' : 'Martiniquais',
    'mauritania' : 'Mauritanian',
    'mauritius' : 'Mauritian',
    'mayotte' : 'Mahoran',
    'mexico' : 'Mexican',
    'micronesia, federated states of' : 'Micronesian',
    'moldova' : 'Moldovan',
    'monaco' : 'Monegasque, Monacan',
    'mongolia' : 'Mongolian',
    'montenegro' : 'Montenegrin',
    'montserrat' : 'Montserratian',
    'morocco' : 'Moroccan',
    'mozambique' : 'Mozambican',
    'namibia' : 'Namibian',
    'nauru' : 'Nauruan',
    'nepal' : 'Nepali',
    'netherlands' : 'Dutch',
    'new caledonia' : 'New Caledonian',
    'new zealand' : 'New Zealand',
    'nicaragua' : 'Nicaraguan',
    'niger' : 'Nigerien',
    'nigeria' : 'Nigerian',
    'niue' : 'Niuean',
    'north korea' : 'North Korean',
    'northern ireland' : 'Northern Irish',
    'northern marianas' : 'Northern Marianan',
    'norway' : 'Norwegian',
    'oman' : 'Omani',
    'pakistan' : 'Pakistani',
    'palau' : 'Palauan',
    'palestine' : 'Palestinian',
    'panama' : 'Panamanian',
    'papua new guinea' : 'Papua New Guinean',
    'paraguay' : 'Paraguayan',
    'people\'s republic of china' : 'Chinese',
    'peru' : 'Peruvian',
    'philippines' : 'Filipino',
    'pitcairn island' : 'Pitcairn Island',
    'poland' : 'Polish',
    'portugal' : 'Portuguese',
    'puerto rico' : 'Puerto Rican',
    'qatar' : 'Qatari',
    'republic of china' : 'Chinese',
    'republic of ireland' : 'Irish',
    'republic of macedonia' : 'Macedonian',
    'republic of the congo' : 'Congolese',
    'romania' : 'Romanian',
    'russia' : 'Russian',
    'rwanda' : 'Rwandan',
    'reunion' : 'Reunionese',
    'saint-pierre and miquelon' : 'Saint-Pierrais/Miquelonnais',
    'samoa' : 'Samoan',
    'san marino' : 'Sammarinese',
    'saudi arabia' : 'Saudi Arabian',
    'scotland' : 'Scottish',
    'senegal' : 'Senegalese',
    'serbia' : 'Serbian',
    'seychelles' : 'Seychellois',
    'sierra leone' : 'Sierra Leonean',
    'singapore' : 'Singapore',
    'slovakia' : 'Slovak',
    'slovenia' : 'Slovenian',
    'solomon islands' : 'Solomon Island',
    'somalia' : 'Somalian',
    'south africa' : 'South African',
    'south korea' : 'South Korean',
    'south ossetia' : 'South Ossetian',
    'south sudan' : 'South Sudanese',
    'spain' : 'Spanish',
    'sri lanka' : 'Sri Lankan',
    'st. helena' : 'St. Helenian',
    'st. kitts and nevis' : 'Kittitian/Vincentian',
    'st. lucia' : 'St. Lucian',
    'st. vincent and the grenadines' : 'St. Vincentian',
    'sudan' : 'Sudanese',
    'surinam' : 'Surinamese',
    'swaziland' : 'Swazi',
    'sweden' : 'Swedish',
    'switzerland' : 'Swiss',
    'syria' : 'Syrian',
    'sao tome and principe' : 'Sao Tomean',
    'taiwan' : 'Taiwanese',
    'tajikistan' : 'Tajikistani',
    'tanzania' : 'Tanzanian',
    'thailand' : 'Thai',
    'togo' : 'Togolese',
    'tonga' : 'Tongan',
    'trinidad and tobago' : 'Trinidadian',
    'tunisia' : 'Tunisian',
    'turkey' : 'Turkish',
    'turkmenistan' : 'Turkmen',
    'turks and caicos islands' : 'none',
    'tuvalu' : 'Tuvaluan',
    'uganda' : 'Ugandan',
    'ukraine' : 'Ukrainian',
    'united arab emirates' : 'Emirati',
    'united kingdom' : 'British',
    'united states' : 'American',
    'uruguay' : 'Uruguayan',
    'uzbekistan' : 'Uzbekistani',
    'vanuatu' : 'Ni-Vanuatu',
    'venezuela' : 'Venezuelan',
    'vietnam' : 'Vietnamese',
    'virgin islands' : 'Virgin Island',
    'wales' : 'Welsh',
    'wallis and futuna' : 'Wallisian/Futunan',
    'western sahara' : 'Sahrawian',
    'yemen' : 'Yemeni',
    'zambia' : 'Zambian',
    'zimbabwe' : 'Zimbabwean'
}

global_list_country = {
    "AF":"Afghanistan",
    "AL":"Albania",
    "DZ":"Algeria",
    "AS":"American Samoa",
    "AD":"Andorra",
    "AO":"Angola",
    "AI":"Anguilla",
    "AQ":"Antarctica",
    "AG":"Antigua and Barbuda",
    "AR":"Argentina",
    "AM":"Armenia",
    "AW":"Aruba",
    "AU":"Australia",
    "AT":"Austria",
    "AZ":"Azerbaijan",
    "BS":"Bahamas",
    "BH":"Bahrain",
    "BD":"Bangladesh",
    "BB":"Barbados",
    "BY":"Belarus",
    "BE":"Belgium",
    "BZ":"Belize",
    "BJ":"Benin",
    "BM":"Bermuda",
    "BT":"Bhutan",
    "BO":"Bolivia",
    "BA":"Bosnia and Herzegovina",
    "BW":"Botswana",
    "BV":"Bouvet Island",
    "BR":"Brazil",
    "BQ":"British Antarctic Territory",
    "IO":"British Indian Ocean Territory",
    "VG":"British Virgin Islands",
    "BN":"Brunei",
    "BG":"Bulgaria",
    "BF":"Burkina Faso",
    "BI":"Burundi",
    "KH":"Cambodia",
    "CM":"Cameroon",
    "CA":"Canada",
    "CT":"Canton and Enderbury Islands",
    "CV":"Cape Verde",
    "KY":"Cayman Islands",
    "CF":"Central African Republic",
    "TD":"Chad",
    "CL":"Chile",
    "CN":"China",
    "CX":"Christmas Island",
    "CC":"Cocos [Keeling] Islands",
    "CO":"Colombia",
    "KM":"Comoros",
    "CG":"Congo - Brazzaville",
    "CD":"Congo - Kinshasa",
    "CK":"Cook Islands",
    "CR":"Costa Rica",
    "HR":"Croatia",
    "CU":"Cuba",
    "CY":"Cyprus",
    "CZ":"Czech Republic",
    "CI":"C\u00f4te d\u2019Ivoire",
    "DK":"Denmark",
    "DJ":"Djibouti",
    "DM":"Dominica",
    "DO":"Dominican Republic",
    "NQ":"Dronning Maud Land",
    "DD":"East Germany",
    "EC":"Ecuador",
    "EG":"Egypt",
    "SV":"El Salvador",
    "GQ":"Equatorial Guinea",
    "ER":"Eritrea",
    "EE":"Estonia",
    "ET":"Ethiopia",
    "FK":"Falkland Islands",
    "FO":"Faroe Islands",
    "FJ":"Fiji",
    "FI":"Finland",
    "FR":"France",
    "GF":"French Guiana",
    "PF":"French Polynesia",
    "TF":"French Southern Territories",
    "FQ":"French Southern and Antarctic Territories",
    "GA":"Gabon",
    "GM":"Gambia",
    "GE":"Georgia",
    "DE":"Germany",
    "GH":"Ghana",
    "GI":"Gibraltar",
    "GR":"Greece",
    "GL":"Greenland",
    "GD":"Grenada",
    "GP":"Guadeloupe",
    "GU":"Guam",
    "GT":"Guatemala",
    "GG":"Guernsey",
    "GN":"Guinea",
    "GW":"Guinea-Bissau",
    "GY":"Guyana",
    "HT":"Haiti",
    "HM":"Heard Island and McDonald Islands",
    "HN":"Honduras",
    "HK":"Hong Kong SAR China",
    "HU":"Hungary",
    "IS":"Iceland",
    "IN":"India",
    "ID":"Indonesia",
    "IR":"Iran",
    "IQ":"Iraq",
    "IE":"Ireland",
    "IM":"Isle of Man",
    "IL":"Israel",
    "IT":"Italy",
    "JM":"Jamaica",
    "JP":"Japan",
    "JE":"Jersey",
    "JT":"Johnston Island",
    "JO":"Jordan",
    "KZ":"Kazakhstan",
    "KE":"Kenya",
    "KI":"Kiribati",
    "KW":"Kuwait",
    "KG":"Kyrgyzstan",
    "LA":"Laos",
    "LV":"Latvia",
    "LB":"Lebanon",
    "LS":"Lesotho",
    "LR":"Liberia",
    "LY":"Libya",
    "LI":"Liechtenstein",
    "LT":"Lithuania",
    "LU":"Luxembourg",
    "MO":"Macau SAR China",
    "MK":"Macedonia",
    "MG":"Madagascar",
    "MW":"Malawi",
    "MY":"Malaysia",
    "MV":"Maldives",
    "ML":"Mali",
    "MT":"Malta",
    "MH":"Marshall Islands",
    "MQ":"Martinique",
    "MR":"Mauritania",
    "MU":"Mauritius",
    "YT":"Mayotte",
    "FX":"Metropolitan France",
    "MX":"Mexico",
    "FM":"Micronesia",
    "MI":"Midway Islands",
    "MD":"Moldova",
    "MC":"Monaco",
    "MN":"Mongolia",
    "ME":"Montenegro",
    "MS":"Montserrat",
    "MA":"Morocco",
    "MZ":"Mozambique",
    "MM":"Myanmar [Burma]",
    "NA":"Namibia",
    "NR":"Nauru",
    "NP":"Nepal",
    "NL":"Netherlands",
    "AN":"Netherlands Antilles",
    "NT":"Neutral Zone",
    "NC":"New Caledonia",
    "NZ":"New Zealand",
    "NI":"Nicaragua",
    "NE":"Niger",
    "NG":"Nigeria",
    "NU":"Niue",
    "NF":"Norfolk Island",
    "KP":"North Korea",
    "VD":"North Vietnam",
    "MP":"Northern Mariana Islands",
    "NO":"Norway",
    "OM":"Oman",
    "PC":"Pacific Islands Trust Territory",
    "PK":"Pakistan",
    "PW":"Palau",
    "PS":"Palestinian Territories",
    "PA":"Panama",
    "PZ":"Panama Canal Zone",
    "PG":"Papua New Guinea",
    "PY":"Paraguay",
    "YD":"People's Democratic Republic of Yemen",
    "PE":"Peru",
    "PH":"Philippines",
    "PN":"Pitcairn Islands",
    "PL":"Poland",
    "PT":"Portugal",
    "PR":"Puerto Rico",
    "QA":"Qatar",
    "RO":"Romania",
    "RU":"Russia",
    "RW":"Rwanda",
    "RE":"R\u00e9union",
    "BL":"Saint Barth\u00e9lemy",
    "SH":"Saint Helena",
    "KN":"Saint Kitts and Nevis",
    "LC":"Saint Lucia",
    "MF":"Saint Martin",
    "PM":"Saint Pierre and Miquelon",
    "VC":"Saint Vincent and the Grenadines",
    "WS":"Samoa",
    "SM":"San Marino",
    "SA":"Saudi Arabia",
    "SN":"Senegal",
    "RS":"Serbia",
    "CS":"Serbia and Montenegro",
    "SC":"Seychelles",
    "SL":"Sierra Leone",
    "SG":"Singapore",
    "SK":"Slovakia",
    "SI":"Slovenia",
    "SB":"Solomon Islands",
    "SO":"Somalia",
    "ZA":"South Africa",
    "GS":"South Georgia and the South Sandwich Islands",
    "KR":"South Korea",
    "ES":"Spain",
    "LK":"Sri Lanka",
    "SD":"Sudan",
    "SR":"Suriname",
    "SJ":"Svalbard and Jan Mayen",
    "SZ":"Swaziland",
    "SE":"Sweden",
    "CH":"Switzerland",
    "SY":"Syria",
    "ST":"S\u00e3o Tom\u00e9 and Pr\u00edncipe",
    "TW":"Taiwan",
    "TJ":"Tajikistan",
    "TZ":"Tanzania",
    "TH":"Thailand",
    "TL":"Timor-Leste",
    "TG":"Togo",
    "TK":"Tokelau",
    "TO":"Tonga",
    "TT":"Trinidad and Tobago",
    "TN":"Tunisia",
    "TR":"Turkey",
    "TM":"Turkmenistan",
    "TC":"Turks and Caicos Islands",
    "TV":"Tuvalu",
    "UM":"U.S. Minor Outlying Islands",
    "PU":"U.S. Miscellaneous Pacific Islands",
    "VI":"U.S. Virgin Islands",
    "UG":"Uganda",
    "UA":"Ukraine",
    "SU":"Union of Soviet Socialist Republics",
    "AE":"United Arab Emirates",
    "GB":"United Kingdom",
    "US":"United States",
    "ZZ":"Unknown or Invalid Region",
    "UY":"Uruguay",
    "UZ":"Uzbekistan",
    "VU":"Vanuatu",
    "VA":"Vatican City",
    "VE":"Venezuela",
    "VN":"Vietnam",
    "WK":"Wake Island",
    "WF":"Wallis and Futuna",
    "EH":"Western Sahara",
    "YE":"Yemen",
    "ZM":"Zambia",
    "ZW":"Zimbabwe",
    "AX":"\u00c5land Islands"
}