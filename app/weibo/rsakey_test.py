# -*- coding: utf-8 -*-
"""
raskey_test.py

Created by <jimokanghanchao@gmail.com> on Dec 10,2015
"""

def main():
  """测试RSAKey类"""
  command_str = """
  python -m pdb rsakey_test.py --servertime 1449716782 --nonce VTEWRH --authcode 009000 --bc
  '102,106,227,219,238,145,162,186,202,101,85,117,71,50,185,177,35,248,193,116,41,141,148,46,196,73,5,199,182,104,254,230,132,108,164,29,221,107,242,16,23,241,13,48,72,93,200,77,190,86,189,206,42,250,8,174,122,172,20,147,92,232,243,91,216,235,95,59,183,192,67,21,224,88,69,125,90,65,113,33,87,165,68,30,212,150,137,24,237,220,124,167,133,152,18,207,244,36,56,231,11,255,109,170,96,222,210,136,14,149,181,112,111,151,157,249,97,158,62,74,1,80,78,228,184,245,82,7,160,180,215,2,126,226,155,135,209,123,127,110,9,115,178,105,142,49,239,154,0,197,128,27,26,118,251,99,32,140,19,208,40,103,213,79,198,54,211,225,134,223,246,102,31,169,234,156,233,129,57,176,53,25,38,34,139,159,17,144,15,166,84,161,130,47,168,175,171,194,131,75,201,179,229,22,253,4,3,188,44,61,60,39,252,89,10,191,28,163,45,138,63,146,12,217,43,100,58,81,173,106,37,52,121,51,153,6,114,187,76,214,64,55,236,204,119,70,195,98,143,66,205,247,94,218,83,240,120,203'
  --bd
  '0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0'
  """
  from argparse import ArgumentParser
  argparser = ArgumentParser(description="测试RSAKey类几个重要的方法\n:%s\n" % (command_str))
  argparser.add_argument("--servertime", type=str, help = "the servertime parameter")
  argparser.add_argument("--nonce", type=str, help = "the nonce parameter")
  argparser.add_argument("--authcode", type=str, help = "the authcode parameter")
  pubkey_default = \
  "EB2A38568661887FA180BDDB5CABD5F21C7BFD59C090CB2D245A87AC253062882729293E5506350508E7F9AA3BB77F4333231490F915F6D63C55FE2F08A49B353F444AD3993CACC02DB784ABBB8E42A9B1BBFFFB38BE18D78E87A0E41B9B8F73A928EE0CCEE1F6739884B9777E4FE9E88A1BBE495927AC4A799B3181D6442443"
  argparser.add_argument("--pubkey", type=str, help = "the pubkey parameter", default=pubkey_default)  
  argparser.add_argument("--string1", type=str, help = "c.toString(16)<==c; like {0:112312,1:9081213,'t':2,'s':0}")
  argparser.add_argument("--bb", type=int, default=256, help = "value of variable bb which is int")
  argparser.add_argument("--bc", type=str, help = "value of variable bc which is an instance of Class Z, like 100,100,23,38,12,90...")
  argparser.add_argument("--bd", type=str, help = "value of variable bd which is an array, like 0,1,2,3,0,5")
  argparser.add_argument("--be", type=int, default=0, help = "value of variable be which is int")

  argparser.print_help()

  args = argparser.parse_args()
  from rsakey import RSAKey, E, bb, bc, be, bd, Z
  rsakey = RSAKey()
  rsakey.setPublic(args.pubkey,'10001')
  if args.string1:
    e = E()
    dict_from_string1 = eval(args.string1)
    e.s = dict_from_string1['s']
    e.t = dict_from_string1['t']
    dict_from_string1.pop('s')
    dict_from_string1.pop('t')
    e.array = dict_from_string1
    print 'toString(16)==>%s' % e.toString(16)
  if args.servertime and args.nonce and args.authcode and args.bc and args.bd:
    bb = args.bb
    be = args.be
    str_to_encrypt = "\t".join([args.servertime, args.nonce]) + "\n" + args.authcode
    bd = [i for i in eval(args.bd)]
    bc_list = [j for j in eval(args.bc)]
    bc = Z()
    bc.i = bc_list[0] 
    bc.j = bc_list[1]
    bc.S = bc_list[2:]
    str_encryption = rsakey.encrypt(str_to_encrypt, bb=bb, bc=bc, bd=bd, be=be)
    print "%s:encrypt()==>%s" % (str_to_encrypt, str_encryption)

if __name__ == '__main__':
  main()

