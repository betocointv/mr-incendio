# -*- coding: utf-8 -*-
"""
Termos de Uso — Mr. Incêndio
"""

import streamlit as st
from db import init_db
from ui import aplicar_tema
from auth import sessao_logada, get_usuario_sessao
from creditos import badge_atual
from ui import nav_inferior, header_usuario

st.set_page_config(page_title="Termos de Uso – Mr. Incêndio", page_icon="📋", layout="wide")
init_db()
aplicar_tema()

if sessao_logada():
    u = get_usuario_sessao()
    if u:
        header_usuario(u["nome"], u["creditos"], u["pontos"], badge_atual(u["pontos"]))

st.markdown("# 📋 Termos de Uso")
st.caption("Última atualização: março de 2026")
st.divider()

st.markdown("""
## 1. Sobre a Plataforma

A plataforma **Mr. Incêndio** é um serviço de consulta automatizada às **Notas Técnicas (NTs)** e normas
técnicas exigidas pelo **Corpo de Bombeiros Militar do Estado do Rio de Janeiro (CBMERJ)**.

O sistema utiliza inteligência artificial para facilitar o acesso e a interpretação das normas oficiais
publicadas pelo CBMERJ, **não substituindo** a análise técnica de profissional habilitado (engenheiro,
arquiteto ou técnico de segurança contra incêndio).

---

## 2. Abrangência e Expansão

### Estado atual
Atualmente a plataforma cobre exclusivamente as normas do **CBMERJ (Rio de Janeiro)**:
- Notas Técnicas (NTs) dos grupos 1 a 5
- COSCIP (Código de Segurança Contra Incêndio e Pânico do Estado do Rio de Janeiro)

### Expansão planejada
A plataforma está em desenvolvimento para incluir normas de outros estados brasileiros, uma vez que
**cada estado possui legislação e normas técnicas próprias** para prevenção e combate a incêndio.
Os próximos estados previstos incluem São Paulo (CBPMESP), Minas Gerais (CBMMG) e Espírito Santo (CBMES).

> ⚠️ **Atenção:** Ao consultar normas de um estado específico, verifique sempre a origem indicada
> nas respostas. Normas de estados diferentes **não são intercambiáveis**.

---

## 3. Limitações e Responsabilidades

### 3.1 Caráter informativo
As respostas geradas pela plataforma têm **caráter exclusivamente informativo e de referência técnica**.
Elas não constituem laudo técnico, parecer profissional, aprovação de projeto nem substituem a
consulta direta ao Corpo de Bombeiros competente.

### 3.2 Precisão das informações
O sistema é treinado com base nas normas vigentes no momento da indexação. O usuário é responsável
por verificar se as normas consultadas estão atualizadas, uma vez que o CBMERJ pode publicar
revisões, errata ou novas NTs a qualquer momento.

### 3.3 Responsabilidade do usuário
O uso das informações obtidas na plataforma para elaboração de projetos, laudos ou qualquer
finalidade técnica ou legal é de **exclusiva responsabilidade do usuário**. A plataforma e seus
mantenedores não se responsabilizam por decisões tomadas com base nas respostas geradas.

### 3.4 Uso profissional
Projetos de prevenção contra incêndio e pânico devem ser elaborados e assinados por profissional
habilitado junto ao CREA ou CAU, conforme legislação vigente.

---

## 4. Créditos e Pagamentos

### 4.1 Sistema de créditos
O acesso ao serviço de consulta é realizado mediante o consumo de **créditos**. Cada consulta
consome 1 (um) crédito do saldo do usuário.

### 4.2 Créditos de boas-vindas
Ao criar uma conta, o usuário recebe **10 créditos gratuitos** para experimentar o sistema.

### 4.3 Validade dos créditos
Os créditos adquiridos **não têm prazo de validade** e podem ser utilizados a qualquer momento,
desde que a conta permaneça ativa.

### 4.4 Não reembolso
Créditos já utilizados em consultas realizadas não são reembolsáveis. Créditos não utilizados
podem ser objeto de reembolso a critério da plataforma, mediante solicitação formal.

### 4.5 Contas empresariais
Contas do tipo **Empresa** exigem cadastro com CNPJ válido. O administrador da empresa é
responsável pelo uso dos créditos por todos os funcionários vinculados à conta.

---

## 5. Pontos e Gamificação

O sistema de pontos e badges tem caráter exclusivamente promocional. Os pontos acumulados podem
ser trocados por créditos conforme as regras vigentes na plataforma, sem valor monetário
e sem possibilidade de saque ou transferência.

---

## 6. Privacidade e Dados

### 6.1 Dados coletados
A plataforma coleta: nome, e-mail, telefone, CPF (conta pessoal) ou CNPJ (conta empresarial),
histórico de consultas e dados de uso da plataforma.

### 6.2 Uso dos dados
Os dados são utilizados exclusivamente para:
- Gerenciamento da conta e autenticação
- Contato relacionado ao serviço
- Melhoria do sistema
- Cumprimento de obrigações legais

### 6.3 Compartilhamento
Os dados não são vendidos ou compartilhados com terceiros, exceto quando exigido por lei ou
autoridade competente.

---

## 7. Propriedade Intelectual

As Notas Técnicas do CBMERJ são documentos públicos de autoria do Corpo de Bombeiros Militar
do Estado do Rio de Janeiro. A plataforma facilita o acesso a esses documentos, sem reivindicar
autoria sobre o conteúdo normativo.

O sistema de busca, interface, código-fonte e demais elementos desenvolvidos para esta plataforma
são propriedade de seus criadores, protegidos pelas leis de propriedade intelectual.

---

## 8. Modificações

Estes Termos de Uso podem ser alterados a qualquer momento. O uso continuado da plataforma após
notificação de alterações constitui aceitação dos novos termos.

---

## 9. Contato

Para dúvidas, sugestões ou solicitações relacionadas a estes termos, entre em contato pelo
e-mail disponibilizado na plataforma.

---

*Ao criar uma conta na plataforma Mr. Incêndio, o usuário declara ter lido, compreendido e
concordado integralmente com estes Termos de Uso.*
""")

st.divider()
if sessao_logada():
    u = get_usuario_sessao()
    if u:
        nav_inferior("", u.get("tipo", "pessoal"))
