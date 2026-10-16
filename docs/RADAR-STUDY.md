# Fork de estudo Radar — LLM Legislativo

Upstream: BaruqueRodrigues/llm-legislativo, commit 6951114da14782ae1433a19f2c4bd1d2442f0ccb. Código MIT de Baruque Rodrigues preservado. Fork solicitado com default_branch_only=false; upstream anuncia apenas main, um commit e nenhum tag na consulta. Main fica intacta; mudanças estão na PR de estudo.

## O que muda

- Checkpoint.pt precisa constar no manifesto; tamanho, digest e metadado científico são conferidos antes/depois do carregamento apropriado. Caminhos, IDs, symlinks estáticos e seletores/latest fora da raiz são recusados. Não é sandbox contra troca concorrente de arquivos.
- Extrator não PDF verifica o SHA-256 do TAR; bundle Colab inclui LICENSE.
- Teste de byte NLL treina seu próprio tokenizer sintético, sem arquivo não versionado. Configuração configs/data/history.yaml foi restaurada com os campos consumidos pelos CLIs e limites de lote. O teste verifica esses limites; R real permanece não executado.
- Treze testes adicionais: dez de checkpoints, dois de publicação e um do perfil restaurado. A suíte tem 179 aprovações e quatro skips em CPU; as duas falhas da auditoria desapareceram.
- Ambiente de validação atualizado e fixado por hashes; CI Python/CPU sem treinamento real ou serviços externos.

## Ambiente e compatibilidade

**Perfil homologado localmente: Linux x86_64, Python 3.12, CPU.** requirements-base.lock aponta para requirements-cpu.lock; não é um lock CUDA. O wheel torch CPU tem URL oficial e hash explícitos; não se adiciona índice global extra de pacotes. Os demais pacotes têm versões/hashes resolvidos via PyPI. NumPy foi atualizado junto ao Arrow para respeitar a ABI exigida em runtime. pyproject.toml sobe os pisos compatíveis com esse estudo; não afirma teste em todas as versões futuras de Python ou bibliotecas.

```sh
python -m pip install --require-hashes --only-binary=:all: -r requirements-cpu.lock
PYTHONPATH=tests/audit:src:. OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 TOKENIZERS_PARALLELISM=false python -m pytest -q
```

Para regenerar o lock, usar uv 0.12.23 e executar scripts/lock_cpu_study.py. A fonte é configs/python/study.in mais o wheel CPU fixado no script; hashes são gerados e devem ser revisados. Regeneração pode escolher versões novas: repetir testes/scan antes de integrar. O lock é gerado; sua revisão parte do input, inventário de versões e validação. O pequeno requirements-base.lock é apenas um encaminhamento documentado.

A auditoria da versão resolvida de 27 pacotes por pip-audit 2.10.1 não encontrou advisories conhecidos na consulta de 16/10/2026. Isso não cobre R/Swift, versões futuras, todo o ambiente de ferramentas, integridade de origem ou exploração. A consulta normaliza torch 2.14.1+cpu para 2.14.1 para busca de advisories da mesma base. O scan não é prova de ausência absoluta de vulnerabilidades.

Build Python wheel aprovado localmente. CI confirma pytest em runner CPU; resultados remotos devem ser lidos na PR. Guard Python em tests/audit/sitecustomize.py recusa sockets externos durante testes e permite loopback; não constitui sandbox do sistema.

## Limites ainda abertos

O reader de corpus upstream continua permitindo modo sem manifesto e não prova sozinho isolamento global de famílias. O estudo original no laboratorio-busca-rag implementa um contrato separado e limitado para esse gate, com dados sintéticos. Não importar corpus real sem revisar tamanho, licença, origem, família/versão e qualidade.

Os pesos publicados no Hugging Face não têm licença declarada pelo mantenedor. Não foram copiados para o fork. Código MIT não autoriza automaticamente os pesos ou todos os anexos do corpus. GPU, macOS/Swift, R, Drive real, treino integral e inferência dos pesos não foram homologados. Não executar integral_colab com o lock CPU como se fosse um ambiente CUDA validado. Nenhuma API paga, n8n ou produção foi conectada.

A extração para Radar é código original de Carlos Felipe nos projetos de busca/avaliação existentes, com referência conceitual ao upstream. Citações permanecem pendentes e não são orientação jurídica. Não há aprovação humana automática nem runtime de agentes novo.

## Revisão e reversão

Revisar nesta ordem: treinamento/checkpoint e persistence; regressões em tests/audit; scripts de publicação; teste de avaliação/perfil YAML; input do lock/gerador; lock gerado e CI. O objetivo único é tornar o fork de estudo verificável em CPU. Runtimes e dados produtivos exigem outra revisão.

Fechar/reverter a PR retorna à main original; não há banco ou serviço alterado. Nenhum merge automático. Dados de treino e checkpoints continuam fora do Git conforme AGENTS.md.
