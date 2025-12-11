# RELATORIO DE MIGRACAO - EXPRESSO EMBUIBE

**Data da Migracao:** 2025-12-09 21:37:30
**Banco Origem:** Embuibe -Peruibe Back End.accdb (SYS3)

---

## RESUMO

| Dados | Quantidade | Observacao |
|-------|------------|------------|
| Clientes/Passageiros | 25,722 | Cadastro unico |
| Historico de Viagens | 75,789 | Vendas realizadas |
| Valor Total Historico | R$ 5,427,427.00 | Soma de todas as vendas |

---

## PERIODO DOS DADOS

- **Primeira venda:** 2016-12-15
- **Ultima venda:** 2025-12-08

---

## ARQUIVOS GERADOS

| Arquivo | Descricao | Registros |
|---------|-----------|-----------|
| clientes_migrar.csv | Clientes para importar | 25,722 |
| historico_viagens.csv | Historico de vendas | 75,789 |
| insert_clientes.sql | SQL de exemplo | 100 |

---

## ESTRUTURA DAS TABELAS DESTINO

### Tabela: clientes
```sql
CREATE TABLE clientes (
    id SERIAL PRIMARY KEY,
    id_legado INTEGER,
    nome VARCHAR(200) NOT NULL,
    telefone1 VARCHAR(20),
    telefone2 VARCHAR(20),
    ponto_referencia TEXT,
    cidade VARCHAR(100) DEFAULT 'PERUIBE',
    uf VARCHAR(2) DEFAULT 'SP',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Tabela: historico_viagens
```sql
CREATE TABLE historico_viagens (
    id SERIAL PRIMARY KEY,
    id_legado INTEGER,
    pedido_id INTEGER,
    cliente_nome VARCHAR(200),
    cliente_telefone VARCHAR(20),
    data_venda DATE,
    valor_unitario DECIMAL(10,2),
    quantidade INTEGER DEFAULT 1,
    valor_total DECIMAL(10,2),
    motorista_id INTEGER,
    placa VARCHAR(20)
);
```

---

## OBSERVACOES

1. **Telefones:** Normalizados para formato (XX) XXXXX-XXXX
2. **Nomes:** Convertidos para maiusculas
3. **Duplicados:** Removidos baseado no telefone principal
4. **Cancelados:** Excluidos do historico

---

*Relatorio gerado automaticamente pelo script de migracao*
