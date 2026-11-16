# Calculo financeiro em Objective-C

Experimento de linha de comando com Foundation e NSDecimalNumber para calcular valor bruto acrescido de taxa decimal entre 0 e 1.

Em macOS: clang -fobjc-arc -framework Foundation labs/objc/TransactionTotal.m -o /tmp/transaction-total
Exemplo: /tmp/transaction-total 100.00 0.10

Requer Foundation da Apple ou adaptacao GNUstep. Projeto isolado do cliente Swift e da API C# existentes.
