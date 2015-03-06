# -*- coding: utf-8 -*-

import os

baseline_dir = 'C:\\CIAN_DATA'

page_file_pattern = "page"
resfile_part_pattern = "RESULT_"
resfile_total_with_txt_pattern = "RESULT_ALL_"
resfile_total_no_txt_pattern = "RESULT_ALL_NOTEXT_"

dirs = {
            'baseline': baseline_dir,
            'msk' : {
                      'rent' : os.path.join(baseline_dir, "MSK\\RENT"),
                      'sell' : os.path.join(baseline_dir, "MSK\\SELL")
                      },
            'msk_region' : {
                      'rent' : os.path.join(baseline_dir, "MSK_REGION\\RENT"),
                      'sell' : os.path.join(baseline_dir, "MSK_REGION\\SELL")
                      }
        }

url_patterns = {
                'msk' : {
                          'rent' : "http://www.cian.ru/cat.php?deal_type=1&obl_id=1&type=4&room<nrooms>=1&p=<npage>",
                          'sell' : "http://www.cian.ru/cat.php?deal_type=2&obl_id=1&type=4&room<nrooms>=1&p=<npage>"
                          },
                'msk_region' : {
                          'rent' : "http://www.cian.ru/cat.php?deal_type=1&obl_id=2&room<nrooms>=1&p=<npage>",
                          'sell' : "http://www.cian.ru/cat.php?deal_type=2&obl_id=2&room<nrooms>=1&p=<npage>"
                          }
            }
