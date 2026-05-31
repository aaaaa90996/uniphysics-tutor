# 大学物理公式表（力学与电磁学）

## 一、力学

### 运动学

| 公式 | 说明 |
|------|------|
| \( \mathbf{v} = d\mathbf{r}/dt \) | 速度定义 |
| \( \mathbf{a} = d\mathbf{v}/dt = d^2\mathbf{r}/dt^2 \) | 加速度定义 |
| \( x = x_0 + v_0 t + \frac{1}{2}at^2 \) | 匀加速位移（仅 a=const） |
| \( v = v_0 + at \) | 匀加速速度 |
| \( v^2 - v_0^2 = 2a(x-x_0) \) | 匀加速速度-位移关系 |
| \( a_c = v^2/r = \omega^2 r \) | 向心加速度 |
| \( a_t = dv/dt = r\alpha \) | 切向加速度 |

### 牛顿定律

| 公式 | 说明 |
|------|------|
| \( \sum\mathbf{F} = m\mathbf{a} \) | 牛顿第二定律（仅惯性系） |
| \( \mathbf{F}_{A\to B} = -\mathbf{F}_{B\to A} \) | 牛顿第三定律 |
| \( f_k = \mu_k N \) | 滑动摩擦力 |
| \( f_s \leq \mu_s N \) | 静摩擦力 |
| \( F = -kx \) | 胡克定律（弹簧） |

### 功和能

| 公式 | 说明 |
|------|------|
| \( W = \int \mathbf{F}\cdot d\mathbf{r} \) | 功的定义 |
| \( K = \frac{1}{2}mv^2 \) | 动能 |
| \( W_{\text{net}} = \Delta K \) | 动能定理 |
| \( U_g = mgy \) | 重力势能 |
| \( U_s = \frac{1}{2}kx^2 \) | 弹性势能 |
| \( \mathbf{F} = -\nabla U \) | 保守力与势能关系 |
| \( E = K + U = \text{const} \) | 机械能守恒（仅保守力） |
| \( W_{\text{nc}} = \Delta E \) | 功能原理 |

### 动量和角动量

| 公式 | 说明 |
|------|------|
| \( \mathbf{p} = m\mathbf{v} \) | 动量 |
| \( \mathbf{J} = \int\mathbf{F}dt = \Delta\mathbf{p} \) | 冲量-动量定理 |
| \( \sum\mathbf{p}_i = \text{const} \) | 动量守恒（合外力=0） |
| \( \mathbf{L} = \mathbf{r}\times\mathbf{p} \) | 角动量 |
| \( \boldsymbol{\tau} = \mathbf{r}\times\mathbf{F} \) | 力矩 |
| \( \sum\boldsymbol{\tau} = d\mathbf{L}/dt \) | 角动量定理 |
| \( \sum\boldsymbol{\tau} = I\alpha \) | 转动定律 |

### 转动

| 公式 | 说明 |
|------|------|
| \( I = \sum m_i r_i^2 = \int r^2 dm \) | 转动惯量 |
| \( I = I_{\text{cm}} + Md^2 \) | 平行轴定理 |
| \( K_{\text{rot}} = \frac{1}{2}I\omega^2 \) | 转动动能 |
| \( v_{\text{cm}} = \omega R \) | 无滑动滚动条件 |

### 简谐振动

| 公式 | 说明 |
|------|------|
| \( x(t) = A\cos(\omega t + \phi) \) | 位移方程 |
| \( v(t) = -A\omega\sin(\omega t + \phi) \) | 速度方程 |
| \( a(t) = -A\omega^2\cos(\omega t + \phi) = -\omega^2 x \) | 加速度方程 |
| \( \omega = \sqrt{k/m} \) | 弹簧振子角频率 |
| \( \omega = \sqrt{g/L} \) | 单摆（小角度近似） |
| \( T = 2\pi/\omega = 1/f \) | 周期 |

## 二、电磁学

### 静电学

| 公式 | 说明 |
|------|------|
| \( \mathbf{F} = \frac{1}{4\pi\varepsilon_0}\frac{q_1 q_2}{r^2}\hat{\mathbf{r}} \) | 库仑定律 |
| \( \mathbf{E} = \mathbf{F}/q_0 \) | 电场定义 |
| \( \oint \mathbf{E}\cdot d\mathbf{A} = Q_{\text{enc}}/\varepsilon_0 \) | 高斯定理（积分形式） |
| \( \nabla\cdot\mathbf{E} = \rho/\varepsilon_0 \) | 高斯定理（微分形式） |
| \( \oint \mathbf{E}\cdot d\mathbf{l} = 0 \) | 静电场环路定理 |
| \( V_b - V_a = -\int_a^b \mathbf{E}\cdot d\mathbf{l} \) | 电势差 |
| \( \mathbf{E} = -\nabla V \) | 电场与电势关系 |
| \( V = \frac{1}{4\pi\varepsilon_0}\frac{q}{r} \) | 点电荷电势 |

### 电容和电流

| 公式 | 说明 |
|------|------|
| \( C = Q/V \) | 电容定义 |
| \( C = \varepsilon_0 A/d \) | 平行板电容 |
| \( U = \frac{1}{2}CV^2 = \frac{Q^2}{2C} \) | 电容器储能 |
| \( I = dQ/dt \) | 电流定义 |
| \( \mathbf{J} = \sigma\mathbf{E} \) | 欧姆定律（微观） |
| \( V = IR \) | 欧姆定律（宏观） |
| \( R = \rho L/A \) | 电阻 |

### 磁场

| 公式 | 说明 |
|------|------|
| \( \mathbf{F} = q\mathbf{v}\times\mathbf{B} \) | 洛伦兹力 |
| \( d\mathbf{F} = I d\mathbf{l}\times\mathbf{B} \) | 安培力 |
| \( \oint \mathbf{B}\cdot d\mathbf{A} = 0 \) | 磁场高斯定理 |
| \( \oint \mathbf{B}\cdot d\mathbf{l} = \mu_0 I_{\text{enc}} \) | 安培环路定理 |
| \( d\mathbf{B} = \frac{\mu_0}{4\pi}\frac{I d\mathbf{l}\times\hat{\mathbf{r}}}{r^2} \) | 毕奥-萨伐尔定律 |

### 电磁感应

| 公式 | 说明 |
|------|------|
| \( \mathcal{E} = -d\Phi_B/dt \) | 法拉第定律 |
| \( \Phi_B = \int\mathbf{B}\cdot d\mathbf{A} \) | 磁通量 |
| \( \mathcal{E} = \oint(\mathbf{v}\times\mathbf{B})\cdot d\mathbf{l} \) | 动生电动势 |
| \( \mathcal{E}_L = -L dI/dt \) | 自感电动势 |
| \( U = \frac{1}{2}LI^2 \) | 电感储能 |

### 麦克斯韦方程组（真空中）

| 公式 | 说明 |
|------|------|
| \( \oint\mathbf{E}\cdot d\mathbf{A} = Q_{\text{enc}}/\varepsilon_0 \) | 高斯定律 |
| \( \oint\mathbf{B}\cdot d\mathbf{A} = 0 \) | 磁高斯定律 |
| \( \oint\mathbf{E}\cdot d\mathbf{l} = -d\Phi_B/dt \) | 法拉第定律 |
| \( \oint\mathbf{B}\cdot d\mathbf{l} = \mu_0 I + \mu_0\varepsilon_0 d\Phi_E/dt \) | 安培-麦克斯韦定律 |

## 三、物理常数

| 常数 | 符号 | 数值 |
|------|------|------|
| 真空介电常数 | \( \varepsilon_0 \) | \( 8.85\times10^{-12}\ \text{F/m} \) |
| 真空磁导率 | \( \mu_0 \) | \( 4\pi\times10^{-7}\ \text{N/A}^2 \) |
| 重力加速度 | \( g \) | \( 9.8\ \text{m/s}^2 \) |
| 电子电荷 | \( e \) | \( 1.60\times10^{-19}\ \text{C} \) |
| 电子质量 | \( m_e \) | \( 9.11\times10^{-31}\ \text{kg} \) |
