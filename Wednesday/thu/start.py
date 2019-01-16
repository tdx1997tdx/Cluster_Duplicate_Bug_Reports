from callstack import CallStackLoader
from field import FieldLoader

# 判断是否为包含关系，暂时判断为 item deep 全等，list size 可不同
class FieldContain:
  def contains(self, field1, field2):
    if len(field1) == 0 or len(field2) == 0: return False
    deep1 = len(field1[0])
    deep2 = len(field2[0])
    if deep1 != deep2: return False
    # list_length = len(field1) if len(field1) < len(field2) else len(field2)
    # deep_length = deep1 # xx if deep1 < deep2 else deep2
    def is_in(_field1, _field2):
      for i in range(0, len(_field1)):
        if _field1[i] not in _field2:
          return False
      return True
    # field1 in field2?
    # field2 in field1?
    return is_in(field1, field2) or is_in(field2, field1)

# 计算两个 field 的重合指数
class FieldIndex:
  def __init__(self):
    self.weights = [41, 37, 31, 29, 23, 19, 17, 13, 11, 7, 5, 3, 2, 1]

  def field_index(self, field1, field2):
    # 计算重合指数
    if len(field1) == 0 or len(field2) == 0: return 0.0
    if field1 == field2: return 1.0
    deep1 = len(field1[0])
    deep2 = len(field2[0])
    # 取 短领域 匹配
    list_length = len(field1) if len(field1) < len(field2) else len(field2)
    deep_length = deep1 if deep1 < deep2 else deep2
    score_weight = self.weights[0-deep_length:]
    # print(score_weight)
    # print(field1)
    # print(field2)
    total_count = 0
    right_count = 0
    for i in range(0, list_length):
      for j in range(0, deep_length):
        total_count += score_weight[j]
        if field1[i][j] == field2[i][j]:
          right_count += score_weight[j]
    return 0.0 if total_count == 0 else right_count/total_count

# 计算两个 callstack 调用链的相似度
class CallStackIndex:
  def calculate(self, callstack1, callstack2):
    return 1




##########################################################################
# START
##########################################################################
# 两辆比较
# 比较两个 stack report 内的第 0 个 stack 信息
# 二次信息（非原始数据，stack.json -> call_data.json + field_data.json）
class Starter:
  def __init__(self):
    self.callStackLoader = CallStackLoader()
    self.fieldLoader = FieldLoader()
    self.c_fieldIndex = FieldIndex()
    self.c_fieldContain = FieldContain()
    self.c_callStackIndex = CallStackIndex()

  # 计算开始
  def calculate(self, report_id1, report_id2):
    call_stacks1 = self.callStackLoader.load_call_stack(report_id1)
    fields1 = self.fieldLoader.load_field(report_id1)
    call_stacks2 = self.callStackLoader.load_call_stack(report_id2)
    fields2 = self.fieldLoader.load_field(report_id2)

    # 暂时只对比两个 report 中各自第一个 stack 数据
    field_info1 = fields1[0]
    field_info2 = fields2[0]
    field1 = field_info1['field']
    field2 = field_info2['field']
    callstack1 = call_stacks1[0]
    callstack2 = call_stacks2[0]
    ## calls
    # 'exception'
    # 'inner'
    # 'outer_pre'
    # 'outer_suf'
    # 'all'
    
    ## field
    # 'field': field_area, # [[]...]
    # 'deep': field_deep, # 3
    # 'interest_field': interest['package'], # org.eclipse.swt
    # 'interest_length': interest['length'], # 38
    # 'interest_start': interest['start_index'], # 0
    # 'interest_end': interest['end_index'] # 37
    def cal_ratio(a, b):
      if b == 0: return 0
      return a / b if a < b else b / a
    return {
      'exception': 1 if callstack1['exception'] == callstack2['exception'] else 0, # exception 是否相同
      # 'exception_msg': 1, # exception message 是否相同
      'field_isdup': 1 if self.c_fieldContain.contains(field1, field2) else 0, # field 是否为包含关系
      'field_dup_index': self.c_fieldIndex.field_index(field1, field2), # field 重合指数，即覆盖率
      'field_deep': cal_ratio(field_info1['deep'], field_info2['deep']), # field 深度 比例，比如：4/5
      'field_length': cal_ratio(len(field1), len(field2)), # field 长度 比例，比如：4/5
      'field_interest_issame': 1 if field_info1['interest_field'] == field_info2['interest_field'] else 0, # 核心 field 区域是否一致，比如：org.eclipse.swt == org.eclipse.swt
      'field_interest_length': cal_ratio(field_info1['interest_length'], field_info2['interest_length']), # 核心 field 区域长度 比例，比如：4/5
      'callstack_inner': self.c_callStackIndex.calculate(callstack1['inner'], callstack2['inner']), # 核心 callstack 区域调用链相似度
      'callstack_outer_1': self.c_callStackIndex.calculate(callstack1['outer_pre'], callstack2['outer_pre']), # 除开核心 callstack 区域，顶部区域相似度
      'callstack_outer_2': self.c_callStackIndex.calculate(callstack1['outer_suf'], callstack2['outer_suf']), # 除开核心 callstack 区域，底部区域相似度
      'callstack_all': self.c_callStackIndex.calculate(callstack1['all'], callstack2['all']), # 全部区域相似度
      'is_dup': -1 # 是否为相同 bug，靠上面所有的数据得出该结论，0 为否，1 为是
    }
    # demo::
    # return {
    #   'exception': 1, # exception 是否相同
    #   # 'exception_msg': 1, # exception message 是否相同
    #   'field_isdup': 1, # field 是否为包含关系
    #   'field_dup_index': 0.82, # field 重合指数，即覆盖率
    #   'field_deep': 1, # field 深度 比例，比如：4/5
    #   'field_length': 1, # field 长度 比例，比如：4/5
    #   'field_interest_issame': 1, # 核心 field 区域是否一致，比如：org.eclipse.swt == org.eclipse.swt
    #   'field_interest_length': 1, # 核心 field 区域长度 比例，比如：4/5
    #   'callstack_inner': 0.83, # 核心 callstack 区域调用链相似度
    #   'callstack_outer_1': 0.8, # 除开核心 callstack 区域，顶部区域相似度
    #   'callstack_outer_2': 0.4, # 除开核心 callstack 区域，底部区域相似度
    #   'callstack_all': 0.7, # 全部区域相似度
    #   'is_dup': 1 # 是否为相同 bug，靠上面所有的数据得出该结论
    # }

def main():
  starter = Starter()
  result = starter.calculate(450135, 450134)
  print(result)

main()