document.addEventListener('DOMContentLoaded', () => {
    fetch('/historico')
    .then(response => response.json())
    .then(data => {
        if (data.status === "success") {
            const tableBody = document.getElementById('historicoTable').getElementsByTagName('tbody')[0];

            // Preenche a tabela com os dados do histórico
            data.data.forEach(row => {
                const newRow = tableBody.insertRow();
                newRow.innerHTML = `
                    <td>${row.númeroprocesso}</td>
                    <td>${row.setoratual}</td>
                    <td>${row.localização_caixa}</td>
                    <td>${row.datacadastro}</td>
                    <td>${row.responsavel}</td>
                `;
            });
        } else {
            alert(data.message);
        }
    })
    .catch(error => {
        alert('Erro ao carregar o histórico: ' + error);
    });
});
