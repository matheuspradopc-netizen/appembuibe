"""
Serviço de Relatórios - Expresso Embuibe
Lógica de negócio para geração de relatórios
"""
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date
from collections import defaultdict
from decimal import Decimal
from ..models.passagem import Passagem
from ..models.viagem import Viagem
from ..models.cliente import Cliente
from ..models.local_embarque import LocalEmbarque
from ..models.cidade import Cidade
from ..models.motorista import Motorista
from ..models.proprietario import Proprietario
from ..schemas.relatorio import (
    RelatorioDiario,
    HorarioRelatorio,
    ViagemRelatorio,
    PassageiroRelatorio,
    RelatorioPeriodo,
    PassagemPeriodo,
    ResumoMotorista,
    ResumoFormaPagamento,
    RelatorioMotorista,
    ViagemMotorista
)


class RelatorioService:
    """Serviço para geração de relatórios"""

    def gerar_relatorio_diario(self, db: Session, data_relatorio: date) -> dict:
        """
        Gera relatório diário SIMPLIFICADO mostrando viagens

        Busca diretamente da tabela viagens (criadas automaticamente ao emitir passagem)

        Args:
            db: Sessão do banco de dados
            data_relatorio: Data do relatório

        Returns:
            Relatório simplificado com lista de viagens
        """
        # Busca todas as viagens do dia ordenadas por horário
        viagens = db.query(Viagem).filter(
            Viagem.data == data_relatorio
        ).order_by(Viagem.horario).all()

        # Monta lista de viagens com dados do motorista e proprietário
        viagens_list = []
        total_passageiros = 0
        total_valor = Decimal('0')

        for viagem in viagens:
            # Busca motorista e proprietário
            motorista = db.query(Motorista).filter(Motorista.id == viagem.motorista_id).first()
            proprietario = db.query(Proprietario).filter(
                Proprietario.id == motorista.proprietario_id
            ).first()

            # Busca passageiros desta viagem (passagens associadas)
            passagens = db.query(Passagem).filter(
                Passagem.data_viagem == viagem.data,
                Passagem.horario == viagem.horario,
                Passagem.motorista_id == viagem.motorista_id
            ).all()

            passageiros_list = []
            for passagem in passagens:
                cliente = db.query(Cliente).filter(Cliente.id == passagem.cliente_id).first()
                local = db.query(LocalEmbarque).filter(LocalEmbarque.id == passagem.local_embarque_id).first()
                cidade = db.query(Cidade).filter(Cidade.id == local.cidade_id).first() if local else None

                passageiros_list.append({
                    "cliente_nome": cliente.nome if cliente else "Desconhecido",
                    "cidade": cidade.nome if cidade else "N/A",
                    "local_embarque": local.nome if local else "N/A",
                    "forma_pagamento": passagem.forma_pagamento or "N/A",
                    "valor": float(passagem.valor) if passagem.valor else 0.0
                })

            viagens_list.append({
                "horario": viagem.horario.strftime("%H:%M"),
                "motorista": motorista.nome,
                "proprietario": proprietario.nome,
                "total_passageiros": viagem.total_passageiros,
                "valor_total": float(viagem.valor_total) if viagem.valor_total else 0.0,
                "status": viagem.status,
                "passageiros": passageiros_list
            })

            total_passageiros += viagem.total_passageiros or 0
            total_valor += viagem.valor_total or Decimal('0')

        return {
            "data": data_relatorio.strftime("%Y-%m-%d"),
            "viagens": viagens_list,
            "total_passageiros": total_passageiros,
            "total_valor": float(total_valor),
            "faturamento_total": float(total_valor),  # Compatibilidade com frontend
            "total_viagens": len(viagens)
        }

    def gerar_relatorio_periodo(
        self,
        db: Session,
        data_inicio: date,
        data_fim: date
    ) -> RelatorioPeriodo:
        """
        Gera relatório por período

        Args:
            db: Sessão do banco de dados
            data_inicio: Data inicial
            data_fim: Data final

        Returns:
            Relatório do período
        """
        # Busca passagens do período (inclui EMITIDA e UTILIZADA para histórico)
        passagens = db.query(Passagem).filter(
            Passagem.data_viagem >= data_inicio,
            Passagem.data_viagem <= data_fim,
            Passagem.status.in_(["EMITIDA", "UTILIZADA"])
        ).order_by(Passagem.data_viagem, Passagem.horario).all()

        # Monta lista de passagens
        passagens_list = []
        resumo_motorista_dict = defaultdict(lambda: {'total': 0, 'valor': Decimal('0'), 'proprietario': ''})
        resumo_pagamento_dict = defaultdict(lambda: {'total': 0, 'valor': Decimal('0')})

        for passagem in passagens:
            motorista = db.query(Motorista).filter(Motorista.id == passagem.motorista_id).first()
            proprietario = db.query(Proprietario).filter(Proprietario.id == motorista.proprietario_id).first()
            cliente = db.query(Cliente).filter(Cliente.id == passagem.cliente_id).first()
            local = db.query(LocalEmbarque).filter(LocalEmbarque.id == passagem.local_embarque_id).first()
            cidade = db.query(Cidade).filter(Cidade.id == local.cidade_id).first()

            passagens_list.append(PassagemPeriodo(
                numero=passagem.numero,
                data_viagem=passagem.data_viagem,
                horario=passagem.horario,
                cliente_nome=cliente.nome,
                motorista_nome=motorista.nome,
                proprietario_nome=proprietario.nome,
                local_embarque=local.nome,
                cidade=cidade.nome,
                valor=passagem.valor,
                forma_pagamento=passagem.forma_pagamento
            ))

            # Atualiza resumos
            resumo_motorista_dict[motorista.nome]['total'] += 1
            resumo_motorista_dict[motorista.nome]['valor'] += passagem.valor
            resumo_motorista_dict[motorista.nome]['proprietario'] = proprietario.nome

            resumo_pagamento_dict[passagem.forma_pagamento]['total'] += 1
            resumo_pagamento_dict[passagem.forma_pagamento]['valor'] += passagem.valor

        # Monta resumos
        resumo_motorista = [
            ResumoMotorista(
                motorista_nome=nome,
                proprietario_nome=data['proprietario'],
                total_passagens=data['total'],
                valor_total=data['valor']
            )
            for nome, data in resumo_motorista_dict.items()
        ]

        resumo_pagamento = [
            ResumoFormaPagamento(
                forma_pagamento=forma,
                total_passagens=data['total'],
                valor_total=data['valor']
            )
            for forma, data in resumo_pagamento_dict.items()
        ]

        total_valor = sum(p.valor for p in passagens_list)

        return RelatorioPeriodo(
            data_inicio=data_inicio,
            data_fim=data_fim,
            passagens=passagens_list,
            total_passagens=len(passagens_list),
            total_passageiros=len(passagens_list),
            valor_total=total_valor,
            resumo_por_motorista=resumo_motorista,
            resumo_por_forma_pagamento=resumo_pagamento
        )

    def gerar_relatorio_motorista(
        self,
        db: Session,
        motorista_id: int,
        data_inicio: date,
        data_fim: date
    ) -> RelatorioMotorista:
        """
        Gera relatório por motorista

        Args:
            db: Sessão do banco de dados
            motorista_id: ID do motorista
            data_inicio: Data inicial
            data_fim: Data final

        Returns:
            Relatório do motorista
        """
        # Busca motorista
        motorista = db.query(Motorista).filter(Motorista.id == motorista_id).first()
        if not motorista:
            raise ValueError("Motorista não encontrado")

        proprietario = db.query(Proprietario).filter(Proprietario.id == motorista.proprietario_id).first()

        # Busca passagens do motorista no período (inclui EMITIDA e UTILIZADA para histórico)
        passagens = db.query(Passagem).filter(
            Passagem.motorista_id == motorista_id,
            Passagem.data_viagem >= data_inicio,
            Passagem.data_viagem <= data_fim,
            Passagem.status.in_(["EMITIDA", "UTILIZADA"])
        ).order_by(Passagem.data_viagem, Passagem.horario).all()

        # Agrupa por data e horário
        viagens_dict = defaultdict(lambda: defaultdict(list))

        for passagem in passagens:
            cliente = db.query(Cliente).filter(Cliente.id == passagem.cliente_id).first()
            local = db.query(LocalEmbarque).filter(LocalEmbarque.id == passagem.local_embarque_id).first()

            viagens_dict[passagem.data_viagem][passagem.horario].append({
                'cliente': cliente.nome,
                'local': local.nome,
                'valor': passagem.valor
            })

        # Monta lista de viagens
        viagens_list = []
        total_passageiros = 0
        valor_total = Decimal('0')

        for data_viagem in sorted(viagens_dict.keys()):
            for horario in sorted(viagens_dict[data_viagem].keys()):
                passageiros_data = viagens_dict[data_viagem][horario]
                total_passageiros_viagem = len(passageiros_data)
                valor_total_viagem = sum(p['valor'] for p in passageiros_data)

                passageiros_lista = [
                    PassageiroRelatorio(
                        nome=p['cliente'],
                        local_embarque=p['local'],
                        valor=p['valor']
                    )
                    for p in passageiros_data
                ]

                viagens_list.append(ViagemMotorista(
                    data=data_viagem,
                    horario=horario,
                    total_passageiros=total_passageiros_viagem,
                    valor_total=valor_total_viagem,
                    passageiros=passageiros_lista
                ))

                total_passageiros += total_passageiros_viagem
                valor_total += valor_total_viagem

        return RelatorioMotorista(
            motorista_nome=motorista.nome,
            proprietario_nome=proprietario.nome,
            data_inicio=data_inicio,
            data_fim=data_fim,
            viagens=viagens_list,
            total_viagens=len(viagens_list),
            total_passageiros=total_passageiros,
            valor_total=valor_total
        )


# Instância global do serviço
relatorio_service = RelatorioService()
