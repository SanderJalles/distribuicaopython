document.addEventListener('DOMContentLoaded', () => {
    const uploadForm = document.getElementById('uploadForm');
    const fileInput = document.getElementById('file'); // Corrigido para id "file"
    const checklistDiv = document.getElementById('checklist');
    const submitButton = document.getElementById('submitButton');
    const checklistButton = document.getElementById('checklistButton');

    // Função para habilitar o botão "Checklist" ao clicar
    checklistButton.addEventListener('click', () => {
        if (fileInput.files.length === 0) {
            alert('Por favor, selecione um arquivo antes de acessar a checklist.');
            return;
        }

        const formData = new FormData();
        formData.append('file', fileInput.files[0]);

        // Enviar o arquivo para validar e redirecionar para a tela de checklist
        fetch('/checklist', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                window.location.href = '/checklist';
            } else {
                alert('Erro: ' + data.message);
            }
        })
        .catch(error => {
            alert('Erro ao processar o arquivo: ' + error);
        });
    });

    // Função para submeter o formulário de upload
    uploadForm.addEventListener('submit', (event) => {
        event.preventDefault(); // Previne o comportamento padrão do formulário

        const formData = new FormData(uploadForm);

        fetch('/upload', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === "warning") {
                alert(data.message + "\nProcessos duplicados: " + (data.duplicados || []).join(", "));
            } else if (data.status === "success") {
                alert("Processos distribuídos com sucesso!");
            } else if (data.status === "error") {
                alert("Erro: " + data.message);
            }
        })
        .catch(error => {
            alert("Erro ao fazer upload: " + error);
        });
    });
});