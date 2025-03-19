document.addEventListener('DOMContentLoaded', function() {
    // Handle current checkbox for dates
    function handleCurrentCheckbox(currentCheckbox, endDateInput) {
        if (currentCheckbox.checked) {
            endDateInput.value = '';
            endDateInput.disabled = true;
        } else {
            endDateInput.disabled = false;
        }
    }

    // Initialize date handling
    document.querySelectorAll('.current-checkbox').forEach(checkbox => {
        const endDateInput = document.querySelector(`#${checkbox.dataset.endDate}`);
        handleCurrentCheckbox(checkbox, endDateInput);
        
        checkbox.addEventListener('change', function() {
            handleCurrentCheckbox(this, endDateInput);
        });
    });

    // Skills handling with tags
    const skillsContainer = document.querySelector('.skills-container');
    const skillInput = document.querySelector('#skill-input');
    const skillsHiddenInput = document.querySelector('#skills');
    
    if (skillInput) {
        skillInput.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' || e.key === ',') {
                e.preventDefault();
                const skill = this.value.trim();
                if (skill) {
                    addSkillTag(skill);
                    this.value = '';
                    updateSkillsHiddenInput();
                }
            }
        });
    }

    function addSkillTag(skill) {
        const tag = document.createElement('span');
        tag.className = 'skill-tag me-2 mb-2';
        tag.innerHTML = `
            ${skill}
            <button type="button" class="btn-close btn-close-white ms-2" aria-label="Remove"></button>
        `;
        
        tag.querySelector('.btn-close').addEventListener('click', function() {
            tag.remove();
            updateSkillsHiddenInput();
        });
        
        skillsContainer.appendChild(tag);
    }

    function updateSkillsHiddenInput() {
        const skills = Array.from(skillsContainer.querySelectorAll('.skill-tag'))
            .map(tag => tag.textContent.trim());
        skillsHiddenInput.value = JSON.stringify(skills);
    }

    // Profile picture preview
    const profilePictureInput = document.querySelector('#id_profile_picture');
    const previewImage = document.querySelector('#profile-picture-preview');
    
    if (profilePictureInput && previewImage) {
        profilePictureInput.addEventListener('change', function() {
            const file = this.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    previewImage.src = e.target.result;
                    previewImage.style.display = 'block';
                };
                reader.readAsDataURL(file);
            }
        });
    }

    // Form validation
    const forms = document.querySelectorAll('.needs-validation');
    forms.forEach(form => {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });
}); 