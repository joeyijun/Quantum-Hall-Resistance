"""
--------------------------- Notice ! ---------------------------------
----------------this file was written for Xinyi-----------------------
----------------------------------------------------------------------
"""
#coding=gbk
import glob, os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.pyplot import MultipleLocator  # 用于设置坐标轴刻度间隔
from scipy import interpolate
from numpy import polyfit
import re
from tkinter import *
import tkinter.filedialog


# 创建新文件夹
def mkdir(path):

    folder = os.path.exists(path)

    if not folder:  # 判断是否存在文件夹如果不存在则创建为文件夹
        os.makedirs(path)  # makedirs 创建文件时如果路径不存在会创建这个路径
        print("---  new folder...  ---")
        print("---  OK  ---")

    else:
        print("---  There is this folder!  ---")


#  文件按名称排序
def atoi(text):
    return int(text) if text.isdigit() else text


def natural_keys(text):
    """
    alist.sort(key=natural_keys) sorts in human order
    http://nedbatchelder.com/blog/200712/human_sorting.html
    (See Toothy's implementation in the comments)
    """
    return [atoi(c) for c in re.split(r'(\d+)', text)]


def SelectPath():
    selectpath_ = tkinter.filedialog.askdirectory()
    selectpath.set(selectpath_)


def RUN():
    global path, V1, V2, ratio, mean_limit, LB
    path = e1.get()
    V1 = e2.get()
    V2 = e3.get()
    ratio = float(e4.get())
    mean_limit = float(e5.get())
    LB = float(e6.get())
    print(path)
    print(V1)
    print(V2)
    print(ratio)
    print(mean_limit)
    print(LB)

root = Tk()
selectpath = StringVar()

Label(root, text="文件夹：").grid(row=0, column=0)
e1 = Entry(root, textvariable=selectpath)
e1.grid(row=0, column=1)
Button(root, text='选择', command=SelectPath).grid(row=0, column=2)

Label(root, text="对称化电压量程：").grid(row=1, column=0)
e2 = Entry(root, textvariable=StringVar(value='1V'))
e2.grid(row=1, column=1)
Label(root, text="拟合范围：").grid(row=2, column=0)  # 默认线性拟合磁场范围为-1T~1T
e6 = Entry(root, textvariable=StringVar(value='0.5'))
e6.grid(row=2, column=1)
Label(root, text="平台电压量程：").grid(row=3, column=0)
e3 = Entry(root, textvariable=StringVar(value='10mV'))
e3.grid(row=3, column=1)
Label(root, text="样品长宽比：").grid(row=4, column=0)
e4 = Entry(root, textvariable=StringVar(value='2'))
e4.grid(row=4, column=1)
Label(root, text="平均值限制：").grid(row=5, column=0)
e5 = Entry(root, textvariable=StringVar(value='0.02'))
e5.grid(row=5, column=1)
Button(root, text='确认', command=RUN).grid(row=6, column=1)
root.mainloop()

path = path.replace('/', '\\\\')+'\\'
mkdir(os.path.join(path, 'New\\'))  # 创建新文件夹
mkdir(os.path.join(path, 'Symmetry\\'))  # 创建新文件夹
mkdir(os.path.join(path, 'Platform\\'))  # 创建新文件夹
files = glob.glob(path+'*.dat')
files.sort(key=natural_keys)   # 文件按名称排序 https://stackoverflow.com/questions/596750
                                # 0/how-to-correctly-sort-a-string-with-a-number-inside/5967539#5967539
df = pd.concat([pd.read_table(fp).assign(Name=os.path.basename(fp), header=None) for fp in files])
df = df.loc[:, ['Field', 'Rxx_X', 'Rxy_X', 'Name']]
linearfit = pd.DataFrame(columns=['Filename', 'current', '斜率', '截距', '载流子浓度', '迁移率'])
platform = pd.DataFrame(columns=['B(T)', 'Rxx', 'Mean', 'Std'])
colors = plt.cm.RdBu(np.linspace(0, 1, 8))  # 渐变色，颜色集为RdBu， 8为数量
i = -1
for file in files:  # 遍历文件
    filename = os.path.basename(file)  # 依次读取文件名
    #print(filename)
    df1 = df[df['Name'] == filename]  # 依据“Name”选取部分行
    df1 = df1.drop(columns=['Name'])  # 删除多余的列
    current = [x for x in filename.split('-') if 'uA' in x][0]  # 取出文件名中的电流
    df1['Rxx_X'] = df1['Rxx_X'] / int(current[:-2]) * 1e6  # 电压除以电流得到电阻，int(current[:-2])为取出电流值
    df1['Rxy_X'] = df1['Rxy_X'] / int(current[:-2]) * 1e6  # 电压除以电流得到电阻
    df1.to_csv(os.path.join(path, 'New\\') + filename, index=False)  # 保存文件
    f = interpolate.interp1d(-df1['Field'], df1['Rxy_X'], kind='linear', bounds_error=False)  # 线性插值，f为函数
    ynew = pd.DataFrame(f(df1['Field']))[0]  # X数据对应的插值数据
    symmetry = (df1['Rxy_X'] - ynew)/2  # 对称化
    sym_df = df1
    sym_df['Rxy_X'] = symmetry
    sym_df.to_csv(os.path.join(path, 'Symmetry\\') + filename, index=False)  # 保存对称化后文件

    volatge = [x for x in filename.split('-') if 'V' in x][0]  # 取出文件名中的电压
    volatge = [x for x in volatge.split('.') if 'V' in x][0]    # 取出文件名中的电压
    if volatge == V1:           # 画出测试电压表量程为x V的数据
        i = i + 1  # color计数
        plt.figure(2)
        plt.plot(df1['Field'], df1['Rxx_X']/1000/ratio, color=colors[i], label=current)
        plt.plot([-9, 9], [0, 0], color='gray', linewidth=0.5, linestyle=":")
        plt.xlabel('B (T)', fontsize=12)
        plt.ylabel(r'$\rho_{xx}$ (k$\Omega$)', fontsize=12)
        plt.legend(loc='upper right')
        plt.figure(3)
        plt.plot(df1['Field'], df1['Rxy_X']/(12906.4035*2), color=colors[i], label=current)
        ax = plt.gca()
        ax.yaxis.set_major_locator(MultipleLocator(0.25))  # y轴刻度间隔设置为0.25的倍数
        plt.plot([-9, 9], [0.5, 0.5], color='gray', linewidth=0.5, linestyle=":")
        plt.plot([-9, 9], [-0.5, -0.5], color='gray', linewidth=0.5, linestyle=":")
        plt.xlabel('B (T)', fontsize=12)
        plt.ylabel(r'$R_{xy}$ ($h/e^2$)', fontsize=12)
        plt.legend(loc='lower right')

        sym_df = sym_df.loc[abs(sym_df['Field']) <= LB]  # 筛选出磁场为正负1 T范围内数据
        if not sym_df.empty:  # 有的数据测的不全，可能没有正负1T数据
            coeff = polyfit(sym_df['Field'], sym_df['Rxy_X'], 1)  # 线性拟合参数，coeff[0]为斜率
            density = 1 / coeff[0] / 1.602 * 1e15
            resistivity = df1.iloc[(df1['Field'] - 0).abs().argsort()[:1]]['Rxx_X']  # B最接近0时的Rxx值
            resistivity = int(resistivity)
            linearfit = linearfit.append([{'Filename': filename, '斜率': coeff[0], '截距': coeff[1],
                                           'current': int(current[:-2]), '载流子浓度': density,
                                           '迁移率': coeff[0] / resistivity * ratio * 1e4}])  # 默认样品长宽比为2
            plt.figure(1)
            plt.plot(sym_df['Field'], sym_df['Rxy_X'], color=colors[i], label=current)
            plt.xlabel('B (T)', fontsize=12)
            plt.ylabel(r'$R_{xy}$ ($\Omega$)', fontsize=12)
            plt.legend(loc='lower right')
    # 找平台
    if volatge == V2:
        accumulative_mean1 = df1['Rxx_X'].expanding(min_periods=10).mean()  # 累计平均，数据间隔10个数据
        accumulative_mean2 = df1['Rxx_X'].iloc[::-1].expanding(min_periods=10).mean()  # 倒序，累计平均
        platform['B(T)'] = pd.concat([df1['Field'][(accumulative_mean1 < mean_limit)],
                                      df1['Field'][(accumulative_mean2 < mean_limit)]], ignore_index=True)
        platform['Rxx'] = pd.concat([df1['Rxx_X'][(accumulative_mean1 < mean_limit)],
                                    df1['Rxx_X'][(accumulative_mean2 < mean_limit)]], ignore_index=True)
        platform['Mean'] = pd.concat([accumulative_mean1[(accumulative_mean1 < mean_limit)],
                                     accumulative_mean2[(accumulative_mean2 < mean_limit)]], ignore_index=True)
        std1 = df1['Rxx_X'][(accumulative_mean1 < mean_limit)].std()  # 第一组数据的标准差
        std2 = df1['Rxx_X'][(accumulative_mean2 < mean_limit)].std()  # 第一组数据的标准差
        plt.figure(4)
        plt.plot(platform['B(T)'], platform['Rxx'], color=colors[i], label=current)
        plt.xlabel('B (T)', fontsize=12)
        plt.ylabel(r'$\rho_{xx}$ ($\Omega$)', fontsize=12)
        plt.legend(loc='center')
        platform.to_csv(os.path.join(path, 'Platform\\') + filename, index=False)

plt.figure(1)
plt.savefig(os.path.join(path, 'New\\') + '\\linear.png', dpi=300, bbox_inches='tight')
plt.figure(2)
plt.savefig(os.path.join(path, 'New\\') + '\\Rxx.png', dpi=300, bbox_inches='tight')
plt.figure(3)
plt.savefig(os.path.join(path, 'New\\') + '\\Rxy.png', dpi=300, bbox_inches='tight')
plt.figure(4)
plt.savefig(os.path.join(path, 'New\\') + '\\platform.png', dpi=300, bbox_inches='tight')
plt.figure(5)
plt.plot(linearfit['current'], linearfit['迁移率'], 'o-')
plt.xlabel(r'I ($\mu$A)', fontsize=12)
plt.ylabel(r'mobility ($cm^2V^{-1}s^{-1}$)', fontsize=12)
plt.savefig(os.path.join(path, 'New\\') + '\\mobility.png', dpi=300, bbox_inches='tight')
linearfit.to_csv(os.path.join(path, 'New\\') + 'linearfit.dat', index=False)  # 保存线性拟合结果
plt.show()
plt.close('all')
