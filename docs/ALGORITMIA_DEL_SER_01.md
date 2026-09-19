# Algoritmia del ser · `A4_ADVANCED`

Doce conceptos, cada uno en tres formas: **el concepto escrito**, **el bloque de
código** y **la construcción matemática**. Nada más. Sin justificación en prosa,
sin cita que no haga una predicción, sin juicio sobre lo que debería existir.

Ámbito: `/home/wis/causal-bench-01`, rama `bench/causal-capability-01`.

## Dimensiones

$$
d_e = 128 \quad d_h = 256 \quad d_m = 128 \quad
d_s = d_e + d_h + d_e + d_m = 640 \quad |\mathcal A| = 25 \quad K_{\text{ens}} = 5
$$

$$
\mathcal A = \{0,\dots,24\},\qquad
a = 5\,\tau + \delta,\quad
\tau \in \{\text{MOVE},\text{PUSH},\text{CONSUME},\text{INSPECT},\text{NOOP}\},\quad
\delta \in \{\uparrow,\downarrow,\leftarrow,\rightarrow,\varnothing\}
$$

Observación: $o_t \in \mathbb R^{4\times 5\times 5}$ (radio de visión $r=2$).
Optimizador: Adam, $\eta = 3\cdot 10^{-4}$, recorte de norma de gradiente.

## Orden del paso

$$
\texttt{perceive}(o_t) \;\to\; \texttt{decide}() \;\to\; \texttt{learn}(\text{transition}_t)
$$

---

# 1 · Percepción

## Concepto

Una red convolucional comprime la ventana egocéntrica a un vector de 128
dimensiones. La entrada son **únicamente** los canales perceptivos. La
observación trae además `mask` (qué celdas de la ventana caen dentro de la
rejilla), `agent_energy` (energía propia normalizada) y `time_fraction`; ninguno
de los tres entra en la convolución. La última capa es una `LayerNorm`, que
resta la media sobre las 128 dimensiones: cualquier señal que desplace las 128
por igual queda eliminada en la salida.

## Código

`terrario/agent/encoder.py:41`

```python
self.conv = nn.Sequential(
    nn.Conv2d(in_channels, 32, kernel_size=3, padding=1),
    nn.ReLU(),
    nn.Conv2d(32, 64, kernel_size=3, padding=1),
    nn.ReLU(),
    nn.Conv2d(64, 64, kernel_size=3, stride=2, padding=1),
    nn.ReLU(),
)
self.head = nn.Sequential(
    nn.Flatten(),
    nn.Linear(flat_dim, latent_dim),
    nn.LayerNorm(latent_dim),
)

def forward(self, x):
    features = self.conv(x)
    out = self.head(features)
    return out
```

`terrario/agent/agents/a4_advanced.py:356`

```python
def perceive(self, observation: Observation) -> None:
    self._last_latent = self.encoder.encode_observation(observation.channels)
    self.homeostasis._energy = observation.agent_energy
```

## Matemática

$$
z^{(1)} = \mathrm{ReLU}\!\left(W^{(1)} * o_t + b^{(1)}\right), \qquad W^{(1)}\in\mathbb R^{32\times 4\times 3\times 3}
$$

$$
z^{(2)} = \mathrm{ReLU}\!\left(W^{(2)} * z^{(1)} + b^{(2)}\right), \qquad W^{(2)}\in\mathbb R^{64\times 32\times 3\times 3}
$$

$$
z^{(3)} = \mathrm{ReLU}\!\left(W^{(3)} *_{s=2} z^{(2)} + b^{(3)}\right), \qquad z^{(3)}\in\mathbb R^{64\times 3\times 3}
$$

$$
\tilde e = W_f\,\mathrm{vec}(z^{(3)}) + b_f, \qquad W_f \in \mathbb R^{128\times 576}
$$

$$
e_t = \gamma \odot \frac{\tilde e - \mu(\tilde e)}{\sqrt{\sigma^2(\tilde e)+\epsilon}} + \beta,
\qquad
\mu(\tilde e) = \frac1{128}\sum_{i=1}^{128}\tilde e_i
$$

Y la inyección que D5.1 propone, con equivalencia al nacer por identidad
aritmética:

$$
o_t^{+} = \big[\,o_t^{\text{ch}}\;;\;\varepsilon_t\cdot\mathbf 1_{5\times5}\,\big] \in \mathbb R^{5\times5\times5},
\qquad
W^{(1)+}_{:,\,1:4} = W^{(1)},\quad W^{(1)+}_{:,\,5} = 0
$$

$$
W^{(1)+}_{:,5}=0 \;\Longrightarrow\; z^{(1)+} \equiv z^{(1)} \;\;\forall \varepsilon_t
\qquad\text{pero}\qquad
\frac{\partial \mathcal L}{\partial W^{(1)+}_{:,5}} = \frac{\partial \mathcal L}{\partial z^{(1)}}\cdot \varepsilon_t \neq 0
$$

---

# 2 · Núcleo temporal

## Concepto

Una celda GRU integra el latente actual con el estado recurrente anterior. El
estado que pasa al paso siguiente se desprende del grafo; la salida que alimenta
las pérdidas de este paso, no. `GRUCore.forward` devuelve el mismo tensor dos
veces, y sólo la referencia guardada en `self._hidden` se desprende. El
resultado exacto: la GRU **sí** se entrena con el gradiente del paso actual, y
**ningún** gradiente cruza de un paso al siguiente.

## Código

`terrario/agent/temporal.py:56`

```python
def forward(self, x: torch.Tensor, h: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
    new_h = self.cell(x, h)
    return new_h, new_h
```

`terrario/agent/agents/a4_advanced.py:405`

```python
self._last_hidden = self._hidden.clone()
if self._use_temporal:
    x = latent.unsqueeze(0)
    output, self._hidden = self.temporal_core(x, self._hidden)
    self._hidden = self._hidden.detach()
    h = output.squeeze(0)
```

## Matemática

$$
r_t = \sigma\!\left(W_{ir}e_t + b_{ir} + W_{hr}h_{t-1} + b_{hr}\right)
$$

$$
u_t = \sigma\!\left(W_{iu}e_t + b_{iu} + W_{hu}h_{t-1} + b_{hu}\right)
$$

$$
n_t = \tanh\!\left(W_{in}e_t + b_{in} + r_t \odot (W_{hn}h_{t-1} + b_{hn})\right)
$$

$$
h_t = (1-u_t)\odot n_t + u_t \odot h_{t-1} \;\in\;\mathbb R^{256}
$$

Con la separación de referencias:

$$
h_t^{\text{grafo}} = h_t, \qquad h_t^{\text{portado}} = \mathrm{sg}[h_t]
$$

donde $\mathrm{sg}[\cdot]$ es el operador de corte de gradiente. Por tanto

$$
\frac{\partial \mathcal L_t}{\partial \theta_{\mathrm{GRU}}} \neq 0
\qquad\text{y}\qquad
\frac{\partial \mathcal L_t}{\partial h_{t-1}} = 0
$$

---

# 3 · Memoria episódica

## Concepto

Un búfer circular guarda quíntuplas de experiencia. La lectura es por contenido:
similitud coseno del latente actual contra todo lo almacenado, se toman los $k$
mejores y se combinan con pesos softmax de esas similitudes. El contexto
devuelto es una media ponderada de embeddings, no de consecuencias: lo que
vuelve es *a qué se parece esto*, no *qué pasó entonces*. La acción, el delta
energético y el error de predicción se escriben y nunca se leen en la ruta de
decisión.

## Código

`terrario/agent/memory.py:42` (escritura) y `:98` (lectura)

```python
entry = {
    "embedding": embedding.detach().clone(),
    "action": action,
    "energy_delta": energy_delta,
    "prediction_error": prediction_error,
    "timestamp": timestamp,
}
if len(self._buffer) < self.capacity:
    self._buffer.append(entry)
else:
    self._buffer[self._write_idx] = entry
self._write_idx = (self._write_idx + 1) % self.capacity
```

```python
stored = torch.stack([e["embedding"] for e in self._buffer])   # (N, dim)
query_norm = F.normalize(query_embedding.unsqueeze(0), dim=-1)
stored_norm = F.normalize(stored, dim=-1)
similarities = (query_norm @ stored_norm.T).squeeze(0)         # (N,)

actual_k = min(k, self.size)
top_vals, top_idx = similarities.topk(actual_k)
retrieved = stored[top_idx]
weights = F.softmax(top_vals, dim=0)
```

`terrario/agent/agents/a4_advanced.py:330`

```python
if self._use_episodic and self.episodic_memory.size > 0:
    retrieved, weights, _ = self.episodic_memory.read(latent, k=5)
    memory_context = (retrieved * weights.unsqueeze(-1)).sum(dim=0)
```

## Matemática

Búfer $\mathcal B_t = \{(\hat e_i, a_i, y_i, \delta_i, \tau_i)\}_{i=1}^{N}$,
escritura circular con índice $w \leftarrow (w+1) \bmod C$.

$$
s_i = \frac{\langle e_t, \hat e_i\rangle}{\lVert e_t\rVert\,\lVert \hat e_i\rVert},
\qquad i = 1,\dots,N
$$

$$
\mathcal K = \operatorname{arg\,top-}k\,(s), \qquad k = 5
$$

$$
w_i = \frac{\exp(s_i)}{\sum_{j\in\mathcal K}\exp(s_j)},\qquad i\in\mathcal K
$$

$$
m_t = \sum_{i \in \mathcal K} w_i\,\hat e_i \;\in\;\mathbb R^{128}
$$

Con relleno a cero cuando $N < k$:
$\;\hat e_i = 0,\; w_i = 0$ para $i > N$, de modo que
$\lVert m_t\rVert$ crece con la ocupación.

---

# 4 · Memoria a largo plazo

## Concepto

Una matriz $M$ de ranuras, leída por atención con consulta el estado recurrente,
y escrita con una regla de puerta que mezcla lo viejo con un producto exterior
de pesos de escritura por valor. Clave y valor son **el mismo vector**, $h_t$:
la memoria se direcciona consigo misma. $M$ es un `nn.Parameter` y está dentro
del optimizador —medido: 58 parámetros, $M$ entre ellos— así que la escriben
**dos rutas**: la copia in-place de la regla de puerta y el paso de Adam.

## Código

`terrario/agent/memory.py:180` (lectura) y `:225` (escritura)

```python
q = self.query_proj(query)            # (batch, dim)
k = self.key_proj(self.M)             # (slots, dim)
scores = q @ k.T / (self.memory_dim ** 0.5)
attn = F.softmax(scores, dim=-1)
context = attn @ self.M
```

```python
k = self.write_key_proj(key)          # (dim,)
v = self.value_proj(value)            # (dim,)
mk = self.key_proj(self.M)            # (slots, dim)
scores = mk @ k / (self.memory_dim ** 0.5)
write_weights = F.softmax(scores, dim=0)
w_gate = torch.sigmoid(self.write_gate(key))

update = torch.outer(write_weights, v)
with torch.no_grad():
    proposed = self.M * (1.0 - w_gate) + update * w_gate
    if torch.isfinite(proposed).all():
        self.M.data.copy_(proposed.clamp(-10.0, 10.0))
```

`terrario/agent/agents/a4_advanced.py:619`

```python
h = self._hidden.squeeze(0) if self._hidden.dim() > 1 else self._hidden
if self.adaptive_freeze.allow("longterm_M"):
    self.longterm_memory.write(h, h)
```

## Matemática

Sea $M \in \mathbb R^{S\times d_m}$. Lectura con consulta $h_t$:

$$
q = W_q h_t,\qquad K = W_k M,\qquad
\alpha = \mathrm{softmax}\!\left(\frac{q K^{\top}}{\sqrt{d_m}}\right) \in \Delta^{S-1}
$$

$$
l_t = \alpha M \;\in\;\mathbb R^{128}
$$

Escritura con clave $=$ valor $= h_t$:

$$
\tilde k = W_{wk} h_t,\qquad v = W_v h_t,\qquad
\beta = \mathrm{softmax}\!\left(\frac{(W_k M)\,\tilde k}{\sqrt{d_m}}\right) \in \Delta^{S-1}
$$

$$
g = \sigma(w_g^{\top} h_t) \in (0,1)
$$

$$
M \;\leftarrow\; \mathrm{clip}\Big[(1-g)\,M + g\,(\beta \otimes v),\; -10,\; 10\Big]
$$

Dos escritores sobre el mismo objeto:

$$
M_{t+1} = \underbrace{\Pi_{[-10,10]}\big((1-g)M_t + g\,\beta v^{\top}\big)}_{\text{regla de puerta, fuera del grafo}}
\quad\text{seguido de}\quad
M \leftarrow \mathrm{Adam}\big(M, \nabla_M \mathcal L\big)
$$

---

# 5 · Estado

## Concepto

El estado sobre el que decide y aprende el organismo es la concatenación de
cuatro vectores: latente perceptivo, recurrente, contexto episódico y contexto
de largo plazo. Los módulos ablacionados contribuyen ceros, de modo que la
dimensión es constante. **No contiene** la energía propia, ni la máscara del
borde del mundo, ni la fracción de tiempo, ni la acción anterior, ni el
resultado motor del paso previo.

## Código

`terrario/agent/agents/a4_advanced.py:315`

```python
def _build_state(self, latent, hidden):
    """s_t = concat(e_t, h_t, memory_context, lt_context)"""
    if self._use_episodic and self.episodic_memory.size > 0:
        retrieved, weights, _ = self.episodic_memory.read(latent, k=5)
        memory_context = (retrieved * weights.unsqueeze(-1)).sum(dim=0)
    else:
        memory_context = torch.zeros(latent_dim, ...)

    if self._use_longterm:
        lt_context, _ = self.longterm_memory.read(hidden)
    else:
        lt_context = torch.zeros(memory_dim, ...)

    state = torch.cat([latent, hidden, memory_context, lt_context])
    return state
```

`terrario/agent/agents/a4_advanced.py:177`

```python
self._state_dim = latent_dim + hidden_dim + latent_dim + memory_dim
```

## Matemática

$$
s_t = \big[\;e_t \;;\; h_t \;;\; m_t \;;\; l_t\;\big] \;\in\;\mathbb R^{640}
$$

$$
m_t = \mathbb 1[\text{episódica}]\cdot\!\!\sum_{i\in\mathcal K}\! w_i \hat e_i,
\qquad
l_t = \mathbb 1[\text{largo plazo}]\cdot \alpha M
$$

La ausencia, escrita como restricción del predictor:

$$
\varepsilon_t \notin \sigma(s_t)
\;\Longrightarrow\;
\hat y(s_t,a) = \mathbb E\big[\,y \mid s_t, a\,\big]
\;\text{ es lo mejor alcanzable, con residuo}\;
\mathbb E\big[\operatorname{Var}(y \mid s_t,a)\big]
$$

---

# 6 · Política y selección de acción

## Concepto

Un perceptrón de dos capas produce 25 logits desde el estado. Se les suma un
bono proporcional a la incertidumbre del ensemble, se dividen por una
temperatura que depende de la energía propia, y se muestrea de la categórica
resultante. Existe además una ruta factorizada —una cabeza de operación y una de
selector— desactivada por defecto.

## Código

`terrario/agent/policy.py:28` y `:60`

```python
self.net = nn.Sequential(
    nn.Linear(state_dim, 256),
    nn.ReLU(),
    nn.Linear(256, TOTAL_ACTIONS),
)

def sample(self, logits, temperature=1.0, generator=None):
    if temperature <= 0:
        temperature = 1e-8
    scaled = logits / temperature
    probs = F.softmax(scaled, dim=-1)
    action = torch.multinomial(probs.detach().cpu(), 1, generator=generator).item()
    log_prob = torch.log(probs[action] + 1e-8)
    return action, log_prob, probs
```

`terrario/agent/agents/a4_advanced.py:427`

```python
temperature = (1.0 + self.homeostasis.exploration_bias) if self._use_homeostasis else 1.0
```

## Matemática

$$
\ell = W_2\,\mathrm{ReLU}(W_1 s_t + b_1) + b_2 \;\in\;\mathbb R^{25}
$$

$$
\ell' = \ell + 0.1\,u, \qquad u_a = \operatorname{Var}_{j\le 5}\big[f_j([s_t;\mathbf 1_a])\big]
$$

$$
T = 1 + (1-\varepsilon_t) = 2 - \varepsilon_t \;\in\;[1,2]
$$

$$
\pi(a \mid s_t) = \frac{\exp(\ell'_a / T)}{\sum_{b\in\mathcal A}\exp(\ell'_b / T)}
$$

$$
a_t \sim \pi(\cdot\mid s_t), \qquad
\log \pi(a_t\mid s_t) = \log\big(\pi_{a_t} + 10^{-8}\big)
$$

Ruta factorizada, desactivada por defecto, con
$a = 5\tau+\delta$:

$$
\log\pi^{\text{fact}}(a) = \log\,\mathrm{softmax}\big(g_{\text{op}}(s_t)\big)_{\tau}
+ \log\,\mathrm{softmax}\big(g_{\text{sel}}(s_t)\big)_{\delta}
$$

---

# 7 · Incertidumbre

## Concepto

Cinco perceptrones independientes predicen el mismo escalar —el delta energético
de la transición— desde estado y acción. La varianza entre sus predicciones se
usa como bono aditivo sobre los logits, evaluada en las 25 acciones antes de
decidir. El nombre del flag es `use_curiosity`; lo que implementa es un bono de
desacuerdo de ensemble, no error de predicción propia convertido en motivo.

## Código

`terrario/agent/uncertainty.py:25` y `:56`

```python
self.heads = nn.ModuleList([
    nn.Sequential(
        nn.Linear(state_dim + action_dim, 128),
        nn.ReLU(),
        nn.Linear(128, 1),
    )
    for _ in range(ensemble_size)
])

x = torch.cat([state, action_onehot], dim=-1)
preds = torch.stack([head(x) for head in self.heads], dim=0)   # (K, batch, 1)
mean = preds.mean(dim=0)
var = preds.var(dim=0, unbiased=False)
```

`terrario/agent/agents/a4_advanced.py:430`

```python
with torch.no_grad():
    uncertainties = torch.zeros(TOTAL_ACTIONS, ...)
    for a in range(TOTAL_ACTIONS):
        a_onehot = self._action_to_onehot(a)
        _, var, _ = self.uncertainty_estimator.predict(state, a_onehot)
        uncertainties[a] = var.mean().item()
    logits = logits + 0.1 * uncertainties
```

## Matemática

$$
x_a = [\,s_t \;;\; \mathbf 1_a\,] \in \mathbb R^{665}
$$

$$
f_j(x_a) = v_j^{\top}\,\mathrm{ReLU}(U_j x_a + c_j) + d_j, \qquad j=1,\dots,5
$$

$$
\bar f(x_a) = \frac15\sum_{j=1}^{5} f_j(x_a),
\qquad
u_a = \frac15\sum_{j=1}^{5}\big(f_j(x_a) - \bar f(x_a)\big)^2
$$

$$
\ell'_a = \ell_a + 0.1\,u_a, \qquad \forall a \in \mathcal A
$$

La pérdida que los entrena, con el mismo objetivo para las cinco cabezas:

$$
\mathcal L_U = \frac15 \sum_{j=1}^{5}\big(f_j(x_{a_t}) - y_t\big)^2
$$

de modo que $u_a \to 0$ conforme las cinco convergen al mismo ajuste.

---

# 8 · Modelo del mundo

## Concepto

Un tronco de dos capas recibe estado y acción concatenados, y de él salen tres
cabezas: el estado siguiente, el delta energético y el logit de terminación. Es
el único predictor de consecuencias del organismo. Su objetivo de estado
siguiente se construye pasando la observación siguiente por el mismo encoder y
la misma GRU, bajo `no_grad`.

## Código

`terrario/agent/world_model.py:32` y `:99`

```python
self.backbone = nn.Sequential(
    nn.Linear(state_dim + action_dim, 256),
    nn.ReLU(),
    nn.Linear(256, 256),
    nn.ReLU(),
)
self.next_state_head = nn.Linear(256, state_dim)
self.energy_head = nn.Linear(256, 1)
self.done_head = nn.Linear(256, 1)

x = torch.cat([state, action_onehot], dim=-1)
features = self.backbone(x)
next_state = self.next_state_head(features)
energy = self.energy_head(features)
done = self.done_head(features)
```

`terrario/agent/world_model.py:110`

```python
loss_state = F.mse_loss(next_state_pred, next_state_target)
loss_energy = F.mse_loss(energy_pred, energy_target)
loss_done = F.binary_cross_entropy_with_logits(done_pred, done_target)
return {..., "loss_total": loss_state + loss_energy + loss_done}
```

## Matemática

$$
x = [\,s\;;\;\mathbf 1_a\,] \in \mathbb R^{665}
$$

$$
\phi = \mathrm{ReLU}\big(V_2\,\mathrm{ReLU}(V_1 x + c_1) + c_2\big) \in \mathbb R^{256}
$$

$$
\hat s' = W_{s}\phi \in \mathbb R^{640},
\qquad
\hat y = w_{\varepsilon}^{\top}\phi \in \mathbb R,
\qquad
\hat d = w_{d}^{\top}\phi \in \mathbb R
$$

$$
\mathcal L_{\mathrm{WM}} =
\underbrace{\tfrac1{640}\lVert \hat s' - s_{t+1}\rVert_2^2}_{\text{estado}}
+ \underbrace{(\hat y - y_t)^2}_{\text{energía}}
+ \underbrace{\mathrm{BCE}\big(\hat d,\;\mathbb 1[\text{done}]\big)}_{\text{terminación}}
$$

con

$$
s_{t+1} = \mathrm{sg}\Big[\big[\,\varphi(o_{t+1});\,\mathrm{GRU}(\varphi(o_{t+1}),h_t);\,m;\,l\,\big]\Big]
$$

---

# 9 · Planner

## Concepto

Disparo aleatorio. Se muestrean $C$ secuencias de $H$ acciones uniformes, se
despliega cada una a través del modelo del mundo acumulando energía predicha y
probabilidad de terminación, se puntúa la secuencia con una combinación lineal
de ambas, y se devuelve **la primera acción** de la mejor. No hay gradiente: es
selección, no aprendizaje. Gana el turno frente a la política con probabilidad
$\tfrac12$.

## Código

`terrario/agent/policy.py:122`

```python
for candidate_idx in range(num_candidates):
    actions = torch.randint(0, TOTAL_ACTIONS, (horizon,), generator=self._generator).tolist()
    sim_state = state.clone()
    total_energy = 0.0
    done_prob_accum = 0.0
    for step, action_int in enumerate(actions):
        action_onehot = torch.zeros(TOTAL_ACTIONS, ...)
        action_onehot[action_int] = 1.0
        next_state, energy_pred, done_pred = world_model(sim_state, action_onehot)
        total_energy += energy_pred.item()
        done_prob = torch.sigmoid(done_pred).item()
        done_prob_accum += done_prob
        sim_state = next_state
        if done_prob > 0.9:
            break
    score = total_energy - 10.0 * done_prob_accum
    if score > best_score:
        best_score = score
        best_action = actions[0]
```

`terrario/agent/agents/a4_advanced.py:528`

```python
if self._use_planner and self._use_world_model:
    planned_action, plan_trace = self.planner.plan(state, self.world_model, ...)
```

## Matemática

Para cada candidato $c = 1,\dots,C$ con $C=10$, $H=5$:

$$
\mathbf a^{(c)} = (a^{(c)}_1,\dots,a^{(c)}_H), \qquad a^{(c)}_j \sim \mathcal U\{0,\dots,24\}
$$

$$
\hat s^{(c)}_0 = s_t, \qquad
\big(\hat s^{(c)}_j,\; \hat y^{(c)}_j,\; \hat d^{(c)}_j\big) = \mathcal W\big(\hat s^{(c)}_{j-1},\, \mathbf 1_{a^{(c)}_j}\big)
$$

con parada anticipada en el primer $j$ tal que $\sigma(\hat d^{(c)}_j) > 0.9$, y

$$
J^{(c)} = \sum_{j=1}^{H_c} \hat y^{(c)}_j \;-\; 10\sum_{j=1}^{H_c} \sigma\big(\hat d^{(c)}_j\big)
$$

$$
c^{\star} = \arg\max_{c} J^{(c)}, \qquad a_t = a^{(c^{\star})}_1
$$

Mezcla con la política:

$$
a_t =
\begin{cases}
a^{(c^\star)}_1 & \text{con probabilidad } \tfrac12\\[4pt]
\sim \pi(\cdot\mid s_t) & \text{con probabilidad } \tfrac12
\end{cases}
$$

---

# 10 · Homeostasis

## Concepto

Un termómetro con dos lecturas derivadas. La energía propia normalizada se fija
en `perceive` y es su única autoridad. De ella salen dos cantidades: el `drive`,
que es la distancia por debajo de un umbral, y el sesgo de exploración, que es
el complemento a uno. El `drive` no tiene ningún consumidor causal: aparece sólo
dentro de diccionarios de traza. El sesgo de exploración tiene exactamente uno:
la temperatura de muestreo.

## Código

`terrario/agent/homeostasis.py:34` y `:44`

```python
@property
def drive(self) -> float:
    """Returns max(0, threshold - energy). Zero when energy is sufficient."""
    return max(0.0, self._threshold - self._energy)

@property
def exploration_bias(self) -> float:
    """Ranges from 0.0 (energy full, no pressure) to 1.0 (energy depleted)."""
    return 1.0 - self._energy
```

`terrario/agent/agents/a4_advanced.py:358` y `:427`

```python
self.homeostasis._energy = observation.agent_energy        # perceive, única autoridad

temperature = (1.0 + self.homeostasis.exploration_bias) if self._use_homeostasis else 1.0
```

## Matemática

$$
\varepsilon_t = \min\!\left(\frac{E_t}{E_{\max}},\,1\right) \in [0,1]
$$

$$
d_t = \max\big(0,\; \theta_h - \varepsilon_t\big), \qquad \theta_h = 0.5
$$

$$
b_t = 1 - \varepsilon_t, \qquad T_t = 1 + b_t = 2 - \varepsilon_t
$$

El grafo causal completo de este módulo:

$$
\varepsilon_t \longrightarrow b_t \longrightarrow T_t \longrightarrow \pi(\cdot\mid s_t)
\qquad\qquad
\varepsilon_t \longrightarrow d_t \longrightarrow \varnothing
$$

---

# 11 · Aprendizaje

## Concepto

Tres pérdidas se suman y se retropropagan juntas en un solo paso de Adam, con
tamaño de lote uno. La pérdida de política es REINFORCE con línea base de media
corrida sobre la recompensa inmediata: no hay función de valor, ni descuento, ni
arranque por bootstrap. El compromiso del optimizador está condicionado a un
permiso de la frontera adaptativa, de modo que el brazo congelado calcula el
mismo gradiente y no lo aplica. La regularización por entropía existe y está
desactivada por defecto.

## Código

`terrario/agent/agents/a4_advanced.py:685`

```python
reward = self._policy_reward(consequence)          # = consequence.energy_delta
if self.adaptive_freeze.allow("energy_baseline"):
    self._baseline_count += 1
    self._energy_baseline += (reward - self._energy_baseline) / self._baseline_count

advantage = reward - self._energy_baseline

fresh_logits = self.policy_head(self._last_state)
fresh_probs = F.softmax(fresh_logits, dim=-1)
fresh_log_prob = torch.log(fresh_probs[self._last_action] + 1e-8)
policy_loss = -fresh_log_prob * advantage

if self._use_entropy_regularization:
    entropy = -(fresh_probs * torch.log(fresh_probs + 1e-8)).sum()
    policy_loss = policy_loss - self._entropy_coefficient * entropy
```

`terrario/agent/learner.py:101` y `:153`

```python
total_loss = sum(losses)
if self._step_count % self.update_frequency != 0:
    return None
if not torch.isfinite(total_loss).all():
    return None

self._optimizer.zero_grad()
total_loss.backward()
torch.nn.utils.clip_grad_norm_(all_params, self.grad_clip)
if commit:
    self._optimizer.step()
```

## Matemática

Recompensa y línea base, con $n_t$ el contador de eventos elegibles:

$$
r_t = y_t, \qquad
n_t = n_{t-1} + 1, \qquad
b_t = b_{t-1} + \frac{r_t - b_{t-1}}{n_t}
$$

$$
A_t = r_t - b_t
$$

Las tres pérdidas:

$$
\mathcal L_\pi = -\log\pi(a_t\mid s_t)\,A_t \;-\; \lambda\,\mathcal H\big(\pi(\cdot\mid s_t)\big),
\qquad \lambda = 0 \text{ por defecto}
$$

$$
\mathcal H(\pi) = -\sum_{a\in\mathcal A}\pi_a\log\pi_a
$$

$$
\mathcal L = \mathcal L_{\mathrm{WM}} + \mathcal L_{U} + \mathcal L_{\pi}
$$

El paso, con recorte global y compromiso condicionado:

$$
g = \nabla_\theta \mathcal L,
\qquad
\tilde g = g \cdot \min\!\left(1, \frac{\kappa}{\lVert g\rVert_2}\right)
$$

$$
\theta_{t+1} =
\begin{cases}
\mathrm{Adam}(\theta_t, \tilde g; \eta = 3\cdot10^{-4}) & \text{si } \texttt{commit}\\[4pt]
\theta_t & \text{si no}
\end{cases}
$$

El gradiente de la política respecto de los logits, que es la forma en que la
actualización toca cada acción:

$$
\nabla_{\ell}\log\pi(a_t) = \mathbf 1_{a_t} - \pi
\qquad\Longrightarrow\qquad
\Delta \ell \;\propto\; A_t\big(\mathbf 1_{a_t} - \pi\big)
$$

y en esperanza sobre $a\sim\pi$, para un subconjunto $\mathcal S\subseteq\mathcal A$
con recompensa constante $r_a = c$:

$$
\frac{\partial J}{\partial \ell_i} = \pi_i\,(r_i - \bar r),
\qquad
\frac{\partial J}{\partial \ell_i} - \frac{\partial J}{\partial \ell_j}
= (\pi_i - \pi_j)(c - \bar r)
\quad \forall i,j \in \mathcal S
$$

---

# 12 · Frontera adaptativa

## Concepto

Cuatro componentes forman el estado que la experiencia modifica: los parámetros,
el búfer episódico, la matriz de largo plazo y la pareja línea-base/contador.
Cada intento de escritura pide permiso y queda registrado, se conceda o no; la
diferencia con revertir es que la escritura bloqueada **no ocurre**. La huella se
construye componente a componente en orden canónico, y excluye $M$ del digest de
parámetros porque físicamente está dentro del optimizador y se contaría dos
veces.

## Código

`terrario/agent/adaptive_freeze.py:106`

```python
def allow(self, component: str, *, phase: str = "learn") -> bool:
    if component not in COMPONENTS:
        raise KeyError(...)
    committed = not self._enabled
    before = self._witness(component) if self._witness else None
    self._attempts.append(WriteAttempt(
        component=component, writer=COMPONENTS[component], phase=phase,
        step=self._step, attempted=True, committed=committed,
        blocked_reason=None if committed else BLOCKED_REASON,
        before_digest=before, after_digest=None))
    return committed
```

`terrario/agent/adaptive_freeze.py:195` y `:246`

```python
CANONICAL_ORDER = ("parameters", "episodic_buffer", "longterm_M", "baseline")
_M_PARAMETER_NAME = "longterm_memory.M"

def adaptive_fingerprint(agent) -> str:
    parts = adaptive_components(agent)
    digest = hashlib.sha256()
    digest.update(ADAPTIVE_FINGERPRINT_VERSION.encode())
    for name in CANONICAL_ORDER:
        digest.update(name.encode())
        digest.update(parts[name])
    return digest.hexdigest()
```

## Matemática

Conjunto adaptativo:

$$
\mathcal C = \big\{\,\theta_{\setminus M},\;\; \mathcal B,\;\; M,\;\; (b, n)\,\big\}
$$

Predicado de escritura, con $\rho$ el régimen:

$$
\mathrm{allow}(c) = \neg\,\mathrm{enabled}(\rho)
\qquad\text{y}\qquad
c_{t+1} =
\begin{cases}
\mathcal U_c(c_t) & \text{si } \mathrm{allow}(c)\\
c_t & \text{si no}
\end{cases}
$$

Huella, con $\Vert$ la concatenación de bytes:

$$
\mathrm{fp}(\text{agente}) = \mathrm{SHA256}\Big(\nu \;\Vert\; \big\Vert_{c\,\in\,\text{orden}} \big(c \;\Vert\; \mathrm{repr}(c)\big)\Big)
$$

$$
\text{orden} = (\theta_{\setminus M},\; \mathcal B,\; M,\; (b,n)),
\qquad \nu = \texttt{"terrario.agent.adaptive-fingerprint/ocf-1"}
$$

Invariante que define el régimen de congelación total:

$$
\text{FULL\_ADAPTIVE\_FREEZE} \iff
\mathrm{fp}(\text{agente}_{t_0}) = \mathrm{fp}(\text{agente}_{t})\quad \forall t > t_0
$$
