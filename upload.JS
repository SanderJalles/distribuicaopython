document.addEventListener('DOMContentLoaded', () => {
    const uploadForm = document.getElementById('uploadForm');
    const fileInput = document.getElementById('fileInput');
    const checklistButton = document.getElementById('checklistButton');

    // Habilitar o botão "Checklist" após o arquivo ser selecionado
    checklistButton.addEventListener('click', () => {
        if (fileInput.files.length === 0) {
            alert('Por favor, selecione um arquivo antes de acessar a checklist.');
            return;
        }

        const formData = new FormData();
        formData.append('file', fileInput.files[0]);

        // Enviar o arquivo para validar e retornar colunas
        fetch('/checklist', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                // Se o arquivo for válido, redirecionar para a página checklist
                window.location.href = '/checklist-page';
            } else {
                alert('Erro: ' + data.message);
            }
        })
        .catch(error => {
            alert('Erro ao processar o arquivo: ' + error);
        });
    });
});

    // Ao submeter o formulário
    uploadForm.addEventListener('submit', (event) => {
        event.preventDefault();

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

