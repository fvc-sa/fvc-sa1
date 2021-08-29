
{
  "name"                 :  "POS Session Report",
  "summary"              :  """This module prints POS Session Reports .""",
  "category"             :  "Point Of Sale",
  "version"              :  "1.0",
  "author"               :  "Rashad Ali",
  "website"              :  "https://api.whatsapp.com/send?phone=967773200611",
  "description"          :  """POS Session Report""",
  "depends"              :  [
                             'point_of_sale',
                             'mail',
                            ],
  "data"                 :  [
                             'views/pos_session_report_view.xml',
                             'views/report_session_summary.xml',
                             'views/pos_session_view.xml',
                             'views/pos_config_view.xml',
                            ],
  "qweb"                 :  ['static/src/xml/pos_session_report.xml'],
  "application"          :  True,
  "installable"          :  True,
  "auto_install"         :  False,
  "pre_init_hook"        :  "pre_init_check",
}