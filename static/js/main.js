// main.js - Основные функции JavaScript для сайта Lost and Found

document.addEventListener('DOMContentLoaded', function() {
    // Инициализация Bootstrap tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Функция для предварительного просмотра изображения при загрузке
    const imageInput = document.getElementById('id_image');
    if (imageInput) {
        const previewContainer = document.createElement('div');
        previewContainer.className = 'mt-3';
        previewContainer.id = 'image-preview-container';
        imageInput.parentNode.insertBefore(previewContainer, imageInput.nextSibling);
        
        imageInput.addEventListener('change', function() {
            previewContainer.innerHTML = '';
            
            if (this.files && this.files[0]) {
                const reader = new FileReader();
                
                reader.onload = function(e) {
                    const preview = document.createElement('img');
                    preview.src = e.target.result;
                    preview.className = 'img-thumbnail';
                    preview.style.maxHeight = '200px';
                    previewContainer.appendChild(preview);
                    
                    const removeButton = document.createElement('button');
                    removeButton.className = 'btn btn-sm btn-danger mt-2';
                    removeButton.textContent = 'Удалить';
                    removeButton.type = 'button';
                    removeButton.addEventListener('click', function() {
                        imageInput.value = '';
                        previewContainer.innerHTML = '';
                    });
                    previewContainer.appendChild(removeButton);
                };
                
                reader.readAsDataURL(this.files[0]);
            }
        });
    }
    
    // Анимация для элементов при прокрутке
    const animateElements = document.querySelectorAll('.animate-on-scroll');
    if (animateElements.length > 0) {
        function checkIfInView() {
            animateElements.forEach(function(element) {
                const rect = element.getBoundingClientRect();
                const windowHeight = window.innerHeight || document.documentElement.clientHeight;
                
                if (rect.top <= windowHeight * 0.8) {
                    element.classList.add('animate__animated', 'animate__fadeInUp');
                }
            });
        }
        
        window.addEventListener('scroll', checkIfInView);
        checkIfInView(); // Проверка при загрузке страницы
    }
    
    // Валидация формы претензии
    const claimForm = document.getElementById('claim-form');
    if (claimForm) {
        claimForm.addEventListener('submit', function(event) {
            const description = document.getElementById('id_description').value.trim();
            const proof = document.getElementById('id_proof').value.trim();
            const contactInfo = document.getElementById('id_contact_info').value.trim();
            
            if (description.length < 10) {
                event.preventDefault();
                alert('Пожалуйста, предоставьте более подробное описание предмета (минимум 10 символов).');
                return false;
            }
            
            if (proof.length < 10) {
                event.preventDefault();
                alert('Пожалуйста, предоставьте более подробное доказательство владения (минимум 10 символов).');
                return false;
            }
            
            if (contactInfo.length < 5) {
                event.preventDefault();
                alert('Пожалуйста, укажите действительную контактную информацию (минимум 5 символов).');
                return false;
            }
        });
    }
    
    // Динамическая фильтрация списка предметов
    const filterForm = document.getElementById('filter-form');
    if (filterForm) {
        const filterInputs = filterForm.querySelectorAll('select, input');
        
        filterInputs.forEach(function(input) {
            input.addEventListener('change', function() {
                filterForm.submit();
            });
        });
    }
    
    // Модальное окно для увеличенного просмотра изображения
    const itemImage = document.querySelector('.item-detail-image');
    if (itemImage) {
        itemImage.addEventListener('click', function() {
            const modal = document.createElement('div');
            modal.className = 'modal fade';
            modal.id = 'imageModal';
            modal.setAttribute('tabindex', '-1');
            modal.setAttribute('aria-hidden', 'true');
            
            modal.innerHTML = `
                <div class="modal-dialog modal-lg modal-dialog-centered">
                    <div class="modal-content">
                        <div class="modal-header">
                            <button type="button" class="close" data-dismiss="modal" aria-label="Close">
                                <span aria-hidden="true">&times;</span>
                            </button>
                        </div>
                        <div class="modal-body p-0">
                            <img src="${this.src}" class="img-fluid" alt="Увеличенное изображение">
                        </div>
                    </div>
                </div>
            `;
            
            document.body.appendChild(modal);
            $('#imageModal').modal('show');
            
            $('#imageModal').on('hidden.bs.modal', function() {
                document.body.removeChild(modal);
            });
        });
    }
});