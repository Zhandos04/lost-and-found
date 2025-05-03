// Улучшенный main.js для Lost and Found

document.addEventListener('DOMContentLoaded', function() {
    // Инициализация элементов Bootstrap
    initBootstrapComponents();
    
    // Функция для предварительного просмотра изображения при загрузке
    initImagePreview();
    
    // Анимация для элементов при прокрутке
    initScrollAnimations();
    
    // Валидация формы
    initFormValidation();
    
    // Динамическая фильтрация списка предметов
    initFilterForm();
    
    // Выделение активного пункта меню
    highlightActiveMenuItem();
    
    // Кнопка возврата наверх
    initBackToTopButton();
});

// Инициализация Bootstrap компонентов
function initBootstrapComponents() {
    // Инициализация tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-toggle="tooltip"]'));
    tooltipTriggerList.forEach(function(tooltipTriggerEl) {
        new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Инициализация поповеров
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-toggle="popover"]'));
    popoverTriggerList.forEach(function(popoverTriggerEl) {
        new bootstrap.Popover(popoverTriggerEl);
    });
}

// Функция предварительного просмотра изображения
function initImagePreview() {
    const imageInput = document.getElementById('id_image');
    if (imageInput) {
        // Создаем контейнер для предпросмотра, если его еще нет
        let previewContainer = document.getElementById('image-preview-container');
        
        if (!previewContainer) {
            previewContainer = document.createElement('div');
            previewContainer.className = 'mt-3';
            previewContainer.id = 'image-preview-container';
            imageInput.parentNode.insertBefore(previewContainer, imageInput.nextSibling);
        }
        
        imageInput.addEventListener('change', function() {
            previewContainer.innerHTML = '';
            
            if (this.files && this.files[0]) {
                const reader = new FileReader();
                
                reader.onload = function(e) {
                    // Создаем превью изображения
                    const previewWrapper = document.createElement('div');
                    previewWrapper.className = 'position-relative';
                    
                    const preview = document.createElement('img');
                    preview.src = e.target.result;
                    preview.className = 'img-thumbnail';
                    preview.style.maxHeight = '200px';
                    previewWrapper.appendChild(preview);
                    
                    // Добавляем кнопку удаления
                    const removeButton = document.createElement('button');
                    removeButton.className = 'btn btn-sm btn-danger position-absolute';
                    removeButton.style.top = '5px';
                    removeButton.style.right = '5px';
                    removeButton.innerHTML = '<i class="fas fa-times"></i>';
                    removeButton.type = 'button';
                    removeButton.addEventListener('click', function() {
                        imageInput.value = '';
                        previewContainer.innerHTML = '';
                    });
                    
                    previewWrapper.appendChild(removeButton);
                    previewContainer.appendChild(previewWrapper);
                    
                    // Добавляем информацию о файле
                    const fileInfo = document.createElement('div');
                    fileInfo.className = 'mt-2 small text-muted';
                    fileInfo.innerHTML = `<i class="fas fa-info-circle mr-1"></i> Файл: ${imageInput.files[0].name} (${formatFileSize(imageInput.files[0].size)})`;
                    previewContainer.appendChild(fileInfo);
                };
                
                reader.readAsDataURL(this.files[0]);
            }
        });
    }
}

// Форматирование размера файла
function formatFileSize(bytes) {
    if (bytes < 1024) return bytes + ' байт';
    else if (bytes < 1048576) return (bytes / 1024).toFixed(1) + ' КБ';
    else return (bytes / 1048576).toFixed(1) + ' МБ';
}

// Анимация элементов при прокрутке
function initScrollAnimations() {
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
}

// Валидация формы
function initFormValidation() {
    // Валидация формы создания/редактирования объявления
    const itemForm = document.querySelector('form[enctype="multipart/form-data"]');
    if (itemForm) {
        itemForm.addEventListener('submit', function(event) {
            const title = document.getElementById('id_title');
            const description = document.getElementById('id_description');
            const contactInfo = document.getElementById('id_contact_info');
            
            let isValid = true;
            
            // Очищаем предыдущие сообщения об ошибках
            document.querySelectorAll('.invalid-feedback').forEach(el => el.remove());
            document.querySelectorAll('.is-invalid').forEach(el => el.classList.remove('is-invalid'));
            
            if (title && title.value.trim().length < 5) {
                showError(title, 'Пожалуйста, введите более подробное название (минимум 5 символов)');
                isValid = false;
            }
            
            if (description && description.value.trim().length < 20) {
                showError(description, 'Пожалуйста, введите более подробное описание (минимум 20 символов)');
                isValid = false;
            }
            
            if (contactInfo && contactInfo.value.trim().length < 5) {
                showError(contactInfo, 'Пожалуйста, укажите действительную контактную информацию (минимум 5 символов)');
                isValid = false;
            }
            
            if (!isValid) {
                event.preventDefault();
            }
        });
    }
    
    // Валидация формы претензии
    const claimForm = document.querySelector('form[action*="claim"]');
    if (claimForm) {
        claimForm.addEventListener('submit', function(event) {
            const description = document.getElementById('id_description');
            const proof = document.getElementById('id_proof');
            const contactInfo = document.getElementById('id_contact_info');
            
            let isValid = true;
            
            // Очищаем предыдущие сообщения об ошибках
            document.querySelectorAll('.invalid-feedback').forEach(el => el.remove());
            document.querySelectorAll('.is-invalid').forEach(el => el.classList.remove('is-invalid'));
            
            if (description && description.value.trim().length < 10) {
                showError(description, 'Пожалуйста, предоставьте более подробное описание предмета (минимум 10 символов)');
                isValid = false;
            }
            
            if (proof && proof.value.trim().length < 10) {
                showError(proof, 'Пожалуйста, предоставьте более подробное доказательство владения (минимум 10 символов)');
                isValid = false;
            }
            
            if (contactInfo && contactInfo.value.trim().length < 5) {
                showError(contactInfo, 'Пожалуйста, укажите действительную контактную информацию (минимум 5 символов)');
                isValid = false;
            }
            
            if (!isValid) {
                event.preventDefault();
            }
        });
    }
}

// Показать сообщение об ошибке для элемента формы
function showError(element, message) {
    element.classList.add('is-invalid');
    
    const feedbackElement = document.createElement('div');
    feedbackElement.className = 'invalid-feedback';
    feedbackElement.textContent = message;
    
    element.parentNode.appendChild(feedbackElement);
}

// Инициализация динамической фильтрации
function initFilterForm() {
    const filterForm = document.getElementById('filter-form');
    if (filterForm) {
        const filterInputs = filterForm.querySelectorAll('select, input[type="date"]');
        
        filterInputs.forEach(function(input) {
            input.addEventListener('change', function() {
                // Если это форма с поисковым запросом, оставляем его значение
                const searchQuery = filterForm.querySelector('input[type="text"]');
                if (searchQuery && searchQuery.value.trim() === '') {
                    // Если нет поискового запроса, отправляем форму
                    filterForm.submit();
                }
            });
        });
    }
}

// Подсветка активного пункта меню
function highlightActiveMenuItem() {
    const currentLocation = window.location.pathname;
    
    document.querySelectorAll('.navbar-nav a.nav-link').forEach(function(link) {
        const linkHref = link.getAttribute('href');
        
        if (currentLocation === linkHref || 
            (currentLocation.startsWith(linkHref) && linkHref !== '/' && linkHref !== '#')) {
            link.classList.add('active');
        }
    });
}

// Кнопка возврата наверх
function initBackToTopButton() {
    const backToTopButton = document.getElementById('backToTop');
    
    if (backToTopButton) {
        // Добавляем стили для кнопки, если их нет в CSS
        if (!backToTopButton.classList.contains('styled')) {
            backToTopButton.style.position = 'fixed';
            backToTopButton.style.bottom = '20px';
            backToTopButton.style.right = '20px';
            backToTopButton.style.zIndex = '99';
            backToTopButton.style.display = 'none';
            backToTopButton.style.width = '40px';
            backToTopButton.style.height = '40px';
            backToTopButton.style.lineHeight = '40px';
            backToTopButton.style.backgroundColor = '#3f72af';
            backToTopButton.style.color = 'white';
            backToTopButton.style.borderRadius = '50%';
            backToTopButton.style.textAlign = 'center';
            backToTopButton.style.boxShadow = '0 2px 10px rgba(0, 0, 0, 0.1)';
            backToTopButton.style.transition = 'all 0.3s ease';
            backToTopButton.classList.add('styled');
        }
        
        // Показываем/скрываем кнопку при прокрутке
        window.addEventListener('scroll', function() {
            if (window.pageYOffset > 300) {
                backToTopButton.style.display = 'block';
            } else {
                backToTopButton.style.display = 'none';
            }
        });
        
        // Плавная прокрутка наверх при клике
        backToTopButton.addEventListener('click', function(e) {
            e.preventDefault();
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        });
    }
}