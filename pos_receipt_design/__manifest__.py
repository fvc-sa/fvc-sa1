
{
  "name"                 :  "POS Receipt Custom Design",
  "summary"              :  """Custom POS Receipt.""",
  "category"             :  "Point Of Sale",
  "version"              :  "1.0.0",
  "author"               :  "RASHAD ALI",
  "website"              :  "https://api.whatsapp.com/send?phone=967773200611",
  "depends"              :  ['point_of_sale','report_qr'],
  "data"                 :  [
                             'security/ir.model.access.csv',
                             'demo/demo.xml',
                             'views/templates.xml',
                             'views/pos_config_view.xml',
                            ],
  "application"          :  True,
  "installable"          :  True,
  "auto_install"         :  False,
}