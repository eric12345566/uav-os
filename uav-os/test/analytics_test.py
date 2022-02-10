import matplotlib.pyplot as plt
import pandas as pd

data = {'state': ['1', '2', '3'],
        'year': ['0', '1', '2']}

data['state'].append('5')
data['year'].append('3')

print(data['state'])

frame = pd.DataFrame(data)

plt.plot(frame.year, frame.state, color='b')
plt.xlabel('year') # 設定x軸標題
plt.title('test') # 設定圖表標題
plt.show()

