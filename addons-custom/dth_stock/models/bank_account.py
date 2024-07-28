from odoo import models, fields, api
from odoo.exceptions import ValidationError
import unicodedata
import re

BANG_XOA_DAU = str.maketrans(
    "ÁÀẢÃẠĂẮẰẲẴẶÂẤẦẨẪẬĐÈÉẺẼẸÊẾỀỂỄỆÍÌỈĨỊÓÒỎÕỌÔỐỒỔỖỘƠỚỜỞỠỢÚÙỦŨỤƯỨỪỬỮỰÝỲỶỸỴáàảãạăắằẳẵặâấầẩẫậđèéẻẽẹêếềểễệíìỉĩịóòỏõọôốồổỗộơớờởỡợúùủũụưứừửữựýỳỷỹỵ",
    "A"*17 + "D" + "E"*11 + "I"*5 + "O"*17 + "U"*11 + "Y"*5 + "a"*17 + "d" + "e"*11 + "i"*5 + "o"*17 + "u"*11 + "y"*5
)

class BankAccount(models.Model):
    _name = 'dth.kho.bank.account'
    _description = 'Tài khoản ngân hàng'

    sim_maker_id = fields.Many2one('dth.kho.sim.maker', string='Thợ sim', ondelete='cascade', index=True)
    bank = fields.Char(string='Ngân hàng', required=True)
    account_number = fields.Char(string='STK Ngân hàng', required=True)
    account_name = fields.Char(string='Tên chủ tài khoản', required=True)
    is_default = fields.Boolean(string='Tài khoản mặc định', default=False)
    
    @api.constrains('account_number')
    def _check_account_number(self):
        for r in self:
            if r.account_number and not self.check_number_format(r.account_number):
                raise ValidationError("Số tài khoản ngân hàng '%s' không hợp lệ. Số tài khoản ngân hàng chỉ được bao gồm các chữ số." % r.account_number)
    
    @api.model_create_multi
    def create(self, vals_list):
        bank_accounts = super(BankAccount, self).create(vals_list)
        for account in bank_accounts:
            if account.is_default:
                account.sim_maker_id.bank_account_ids.filtered(lambda r: r.id != account.id).is_default = False
        return bank_accounts

    def write(self, vals):
        if 'account_name' in vals:
            vals['account_name'] = self.remove_accents(vals['account_name']).upper()
        res = super(BankAccount, self).write(vals)
        if vals.get('is_default', False):
            other_banks = self.sim_maker_id.bank_account_ids - self
            other_banks.filtered(lambda bank: bank.is_default).write({'is_default': False})
        return res
    
    @api.model
    def create(self, vals):
        if 'account_name' in vals:
            vals['account_name'] = self.remove_accents(vals['account_name']).upper()
        account = super(BankAccount, self).create(vals)
        if account.is_default:
            account.sim_maker_id.bank_account_ids.filtered(lambda r: r.id != account.id).is_default = False
        return account
    
    def check_number_format(self, str):
        regex = r'^[0-9]+$'
        if re.match(regex, str):
            return True
        else:
            return False
    
    def remove_accents(self, str):
        if not unicodedata.is_normalized("NFC", str):
            str = unicodedata.normalize("NFC", str)
        return str.translate(BANG_XOA_DAU)
    
