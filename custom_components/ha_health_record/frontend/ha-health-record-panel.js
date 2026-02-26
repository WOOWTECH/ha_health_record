// Custom panel using vanilla web components (no external dependencies)
class HaHealthRecordPanel extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
    this._hass = null;
    this.members = [];
    this.records = [];
    this.loading = true;
    this.startDate = '';
    this.endDate = '';
    this.showInputDialog = false;
    this.selectedMember = null;
    this.selectedType = '';
    this.inputValue = 0;
    this.inputNote = '';
    this.submitting = false;

    // Timestamp for logging (defaults to now)
    this.inputTimestamp = '';

    // Tab state
    this.activeTab = 'record'; // 'record' | 'settings'
    this.settingsSubTab = 'members'; // 'members' | 'recordTypes'
    this.expandedRecordId = null;
    this.editingRecord = null; // { value, note, timestamp }
    this.showTypeDialog = false;
    this.editingType = null; // { mode: 'add'|'edit', data: {...} }
    this.showMemberDialog = false;
    this.editingMember = null; // { mode: 'add'|'edit', data: {...} }
    this.showDeleteConfirm = false;
    this.deleteTarget = null; // { type: 'record'|'recordType'|'member', id, name, memberId? }

    // New: Selected member for filtering (like Finance Record's account selector)
    this.selectedMemberId = '';

    // New: Search query
    this.searchQuery = '';

    // Localization strings
    this._strings = {
      en: {
        // Header
        title: 'Health Record',
        filter: 'Filter',
        to: 'to',
        search: 'Search...',
        allMembers: 'All Members',
        selectMember: 'Select Member',
        // Tabs
        record: 'Record',
        settings: 'Settings',
        // Sub-tabs
        recordTypes: 'Record Types',
        members: 'Members',
        // Timeline
        noMembers: 'No members configured. Go to the Settings tab to add members.',
        noRecords: 'No records for this date range.',
        // Manage
        noMembersManage: 'No members configured. Add a member first.',
        noRecordTypes: 'No record types configured for this member.',
        noMembersYet: 'No members configured yet.',
        member: 'Member',
        unit: 'Unit',
        current: 'Current',
        records_label: 'Records',
        // Buttons
        addRecordType: '+ Add Record Type',
        addMember: '+ Add Member',
        save: 'Save',
        saving: 'Saving...',
        cancel: 'Cancel',
        delete: 'Delete',
        deleting: 'Deleting...',
        // Dialogs
        logFor: 'Log {type} for {name}',
        value: 'Value',
        note: 'Note',
        optionalNote: 'Optional note',
        timestamp: 'Time',
        now: 'Now',
        addRecordTypeTitle: 'Add Record Type',
        editRecordTypeTitle: 'Edit Record Type',
        addMemberTitle: 'Add Member',
        editMemberTitle: 'Edit Member',
        name: 'Name',
        namePlaceholder: 'e.g., Feeding',
        unitPlaceholder: 'e.g., ml',
        defaultValue: 'Default Value',
        memberNamePlaceholder: 'e.g., Baby Emma',
        memberIdLabel: 'ID (optional, auto-generated from name)',
        memberIdPlaceholder: 'e.g., baby_emma',
        memberNoteLabel: 'Note',
        memberNotePlaceholder: 'Optional notes about this member',
        confirmDelete: 'Confirm Delete',
        confirmDeleteMessage: 'Are you sure you want to delete "{name}"?',
        loading: 'Loading...',
        menu: 'Menu',
        totalRecords: 'Total Records',
        lastRecord: 'Last Record',
        noRecordsYet: 'No records yet',
        recordTypesCount: 'Record Types',
      },
      'zh-Hant': {
        // Header
        title: '健康紀錄',
        filter: '篩選',
        to: '至',
        search: '搜尋...',
        allMembers: '所有成員',
        selectMember: '選擇成員',
        // Tabs
        record: '紀錄',
        settings: '設定',
        // Sub-tabs
        recordTypes: '紀錄類型',
        members: '成員',
        // Timeline
        noMembers: '尚未設定成員。請前往「設定」分頁新增成員。',
        noRecords: '此日期範圍內沒有紀錄。',
        // Manage
        noMembersManage: '尚未設定成員。請先新增成員。',
        noRecordTypes: '此成員尚未設定紀錄類型。',
        noMembersYet: '尚未設定任何成員。',
        member: '成員',
        unit: '單位',
        current: '目前',
        records_label: '紀錄',
        // Buttons
        addRecordType: '+ 新增紀錄類型',
        addMember: '+ 新增成員',
        save: '儲存',
        saving: '儲存中...',
        cancel: '取消',
        delete: '刪除',
        deleting: '刪除中...',
        // Dialogs
        logFor: '為 {name} 記錄 {type}',
        value: '數值',
        note: '備註',
        optionalNote: '選填備註',
        timestamp: '時間',
        now: '現在',
        addRecordTypeTitle: '新增紀錄類型',
        editRecordTypeTitle: '編輯紀錄類型',
        addMemberTitle: '新增成員',
        editMemberTitle: '編輯成員',
        name: '名稱',
        namePlaceholder: '例如：餵食',
        unitPlaceholder: '例如：ml',
        defaultValue: '預設數值',
        memberNamePlaceholder: '例如：寶寶小明',
        memberIdLabel: 'ID（選填，將自動從名稱產生）',
        memberIdPlaceholder: '例如：baby_ming',
        memberNoteLabel: '備註',
        memberNotePlaceholder: '關於此成員的選填備註',
        confirmDelete: '確認刪除',
        confirmDeleteMessage: '確定要刪除「{name}」嗎？',
        loading: '載入中...',
        menu: '選單',
        totalRecords: '總紀錄數',
        lastRecord: '最新紀錄',
        noRecordsYet: '尚無紀錄',
        recordTypesCount: '紀錄類型',
      },
      'zh-Hans': {
        // Header
        title: '健康记录',
        filter: '筛选',
        to: '至',
        search: '搜索...',
        allMembers: '所有成员',
        selectMember: '选择成员',
        // Tabs
        record: '记录',
        settings: '设置',
        // Sub-tabs
        recordTypes: '记录类型',
        members: '成员',
        // Timeline
        noMembers: '尚未设置成员。请前往"设置"标签页添加成员。',
        noRecords: '此日期范围内没有记录。',
        // Manage
        noMembersManage: '尚未设置成员。请先添加成员。',
        noRecordTypes: '此成员尚未设置记录类型。',
        noMembersYet: '尚未设置任何成员。',
        member: '成员',
        unit: '单位',
        current: '当前',
        records_label: '记录',
        // Buttons
        addRecordType: '+ 添加记录类型',
        addMember: '+ 添加成员',
        save: '保存',
        saving: '保存中...',
        cancel: '取消',
        delete: '删除',
        deleting: '删除中...',
        // Dialogs
        logFor: '为 {name} 记录 {type}',
        value: '数值',
        note: '备注',
        optionalNote: '可选备注',
        timestamp: '时间',
        now: '现在',
        addRecordTypeTitle: '添加记录类型',
        editRecordTypeTitle: '编辑记录类型',
        addMemberTitle: '添加成员',
        editMemberTitle: '编辑成员',
        name: '名称',
        namePlaceholder: '例如：喂食',
        unitPlaceholder: '例如：ml',
        defaultValue: '默认数值',
        memberNamePlaceholder: '例如：宝宝小明',
        memberIdLabel: 'ID（可选，将自动从名称生成）',
        memberIdPlaceholder: '例如：baby_ming',
        memberNoteLabel: '备注',
        memberNotePlaceholder: '关于此成员的可选备注',
        confirmDelete: '确认删除',
        confirmDeleteMessage: '确定要删除"{name}"吗？',
        loading: '加载中...',
        menu: '菜单',
        totalRecords: '总记录数',
        lastRecord: '最新记录',
        noRecordsYet: '尚无记录',
        recordTypesCount: '记录类型',
      },
    };

    // Initialize dates
    const now = new Date();
    const startOfDay = new Date(now.getFullYear(), now.getMonth(), now.getDate(), 0, 0, 0);
    const endOfDay = new Date(now.getFullYear(), now.getMonth(), now.getDate(), 23, 59, 59, 999);
    this.startDate = this._toLocalISOString(startOfDay);
    this.endDate = this._toLocalISOString(endOfDay);
  }

  // Get localized string
  _t(key, replacements = {}) {
    const lang = this._getLanguage();
    const strings = this._strings[lang] || this._strings['en'];
    let str = strings[key] || this._strings['en'][key] || key;

    // Replace placeholders like {name}, {type}
    for (const [k, v] of Object.entries(replacements)) {
      str = str.replace(new RegExp(`\\{${k}\\}`, 'g'), v);
    }
    return str;
  }

  // Get current language, with fallback
  _getLanguage() {
    const locale = this._hass?.locale?.language || navigator.language || 'en';
    // Check for exact match first
    if (this._strings[locale]) return locale;
    // Check for language prefix (e.g., 'zh-TW' -> 'zh-Hant')
    if (locale.startsWith('zh-TW') || locale.startsWith('zh-HK')) return 'zh-Hant';
    if (locale.startsWith('zh-CN') || locale.startsWith('zh-SG')) return 'zh-Hans';
    if (locale.startsWith('zh')) return 'zh-Hans'; // Default Chinese to Simplified
    return 'en';
  }

  set hass(hass) {
    this._hass = hass;
    if (hass && this.members.length === 0) {
      this._loadData();
    }
  }

  get hass() {
    return this._hass;
  }

  connectedCallback() {
    this._render();
  }

  _getLocale() {
    return this._hass?.locale?.language || navigator.language || 'en';
  }

  _toLocalISOString(date) {
    const pad = (n) => n.toString().padStart(2, '0');
    return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}T${pad(date.getHours())}:${pad(date.getMinutes())}`;
  }

  async _loadData() {
    this.loading = true;
    this._render();

    try {
      // Load members
      const membersResult = await this._hass.callWS({
        type: 'ha_health_record/get_members',
      });
      this.members = membersResult.members || [];

      // Auto-select first member if none selected
      if (this.members.length > 0 && !this.selectedMemberId) {
        this.selectedMemberId = this.members[0].id;
      }

      // Load records
      await this._loadRecords();
    } catch (error) {
      console.error('Error loading data:', error);
    }

    this.loading = false;
    this._render();
  }

  async _loadRecords() {
    try {
      const recordsResult = await this._hass.callWS({
        type: 'ha_health_record/get_records',
        start_time: new Date(this.startDate).toISOString(),
        end_time: new Date(this.endDate).toISOString(),
      });
      this.records = recordsResult.records || [];
    } catch (error) {
      console.error('Error loading records:', error);
    }
    this._render();
  }

  _formatTime(dateStr) {
    const date = new Date(dateStr);
    return date.toLocaleTimeString(this._getLocale(), {
      hour: '2-digit',
      minute: '2-digit',
    });
  }

  _formatDate(dateStr) {
    const date = new Date(dateStr);
    return date.toLocaleDateString(this._getLocale(), {
      month: 'short',
      day: 'numeric',
    });
  }

  _generateRecordId(record) {
    // Use UUID if available, otherwise fall back to composite key
    if (record.id) return record.id;
    return `${record.member_id}_${record.record_type}_${record.timestamp}`;
  }

  _openInputDialog(member, recordType) {
    this.selectedMember = member;
    this.selectedType = recordType;
    const typeInfo = (member.record_sets || []).find(s => s.type === recordType);
    this.inputValue = typeInfo?.current_value || 0;
    this.inputNote = '';
    this.inputTimestamp = this._toLocalISOString(new Date());
    this.showInputDialog = true;
    this._render();
  }

  _closeInputDialog() {
    this.showInputDialog = false;
    this.selectedMember = null;
    this.selectedType = '';
    this._render();
  }

  async _submitInput() {
    if (!this.selectedMember || !this.selectedType || this.submitting) return;

    this.submitting = true;
    this._render();

    try {
      await this._hass.callWS({
        type: 'ha_health_record/log_record',
        member_id: this.selectedMember.id,
        record_type: this.selectedType,
        value: this.inputValue || 0,
        note: this.inputNote || '',
        timestamp: this.inputTimestamp ? new Date(this.inputTimestamp).toISOString() : undefined,
      });

      this._closeInputDialog();
      await this._loadRecords();
    } catch (error) {
      console.error('Error logging record:', error);
      alert('Failed to log record: ' + error.message);
    }

    this.submitting = false;
    this._render();
  }

  _handleDateChange() {
    const startInput = this.shadowRoot.querySelector('#start-date');
    const endInput = this.shadowRoot.querySelector('#end-date');
    if (startInput && endInput) {
      this.startDate = startInput.value;
      this.endDate = endInput.value;
      this._loadRecords();
    }
  }

  // Toggle sidebar
  _toggleSidebar() {
    this.dispatchEvent(new CustomEvent("hass-toggle-menu", { bubbles: true, composed: true }));
  }

  // Member selector change
  _onMemberChange(e) {
    this.selectedMemberId = e.target.value;
    this._render();
  }

  // Search input change
  _onSearchInput(e) {
    this.searchQuery = e.target.value;
    this._render();
  }

  // Get filtered records based on member and search
  _getFilteredRecords() {
    let filtered = [...this.records];

    // Filter by selected member
    if (this.selectedMemberId) {
      filtered = filtered.filter(r => r.member_id === this.selectedMemberId);
    }

    // Filter by search query
    if (this.searchQuery && this.searchQuery.trim()) {
      const query = this.searchQuery.toLowerCase().trim();
      filtered = filtered.filter(r => {
        const note = (r.note || '').toLowerCase();
        const typeName = (r.record_name || r.record_type || '').toLowerCase();
        const memberName = (r.member_name || '').toLowerCase();
        const val = String(r.value || '');
        return note.includes(query) || typeName.includes(query) || memberName.includes(query) || val.includes(query);
      });
    }

    return filtered;
  }

  // ============================================================================
  // Tab Navigation
  // ============================================================================

  _switchTab(tab) {
    this.activeTab = tab;
    this._render();
  }

  _switchSettingsSubTab(subTab) {
    this.settingsSubTab = subTab;
    this._render();
  }

  // ============================================================================
  // Inline Record Editing
  // ============================================================================

  _toggleRecordExpand(record) {
    const recordId = this._generateRecordId(record);
    if (this.expandedRecordId === recordId) {
      this.expandedRecordId = null;
      this.editingRecord = null;
    } else {
      this.expandedRecordId = recordId;
      // Convert ISO timestamp to datetime-local format
      const timestamp = record.timestamp ? this._toLocalISOString(new Date(record.timestamp)) : '';
      this.editingRecord = {
        value: record.value || 0,
        note: record.note || '',
        timestamp: timestamp,
      };
    }
    this._render();
  }

  async _saveRecordEdit(record) {
    if (this.submitting) return;
    this.submitting = true;
    this._render();

    try {
      // Convert datetime-local value to ISO string for new_timestamp
      const newTimestamp = this.editingRecord.timestamp ? new Date(this.editingRecord.timestamp).toISOString() : null;
      await this._hass.callWS({
        type: 'ha_health_record/update_record',
        member_id: record.member_id,
        type_id: record.record_type,
        timestamp: record.timestamp,
        ...(record.id ? { record_id: record.id } : {}),
        value: this.editingRecord.value,
        note: this.editingRecord.note,
        ...(newTimestamp && newTimestamp !== record.timestamp ? { new_timestamp: newTimestamp } : {}),
      });

      this.expandedRecordId = null;
      this.editingRecord = null;
      await this._loadRecords();
    } catch (error) {
      console.error('Error updating record:', error);
      alert('Failed to update record: ' + error.message);
    }

    this.submitting = false;
    this._render();
  }

  _cancelRecordEdit() {
    this.expandedRecordId = null;
    this.editingRecord = null;
    this._render();
  }

  _showDeleteRecordConfirm(record) {
    this.deleteTarget = {
      type: 'record',
      id: this._generateRecordId(record),
      name: `${record.record_name || record.record_type} record`,
      record: record,
    };
    this.showDeleteConfirm = true;
    this._render();
  }

  // ============================================================================
  // Type Management (unified Record Types)
  // ============================================================================

  _openAddTypeDialog() {
    this.editingType = {
      mode: 'add',
      memberId: this.selectedMemberId || this.members[0]?.id || '',
      data: { name: '', unit: '', default_value: 0 },
    };
    this.showTypeDialog = true;
    this._render();
  }

  _openEditTypeDialog(memberId, typeData) {
    this.editingType = {
      mode: 'edit',
      memberId: memberId,
      typeId: typeData.type,
      data: {
        name: typeData.name,
        unit: typeData.unit,
        default_value: typeData.current_value || 0,
      },
    };
    this.showTypeDialog = true;
    this._render();
  }

  _closeTypeDialog() {
    this.showTypeDialog = false;
    this.editingType = null;
    this._render();
  }

  async _saveType() {
    if (this.submitting || !this.editingType) return;
    this.submitting = true;
    this._render();

    try {
      const { mode, memberId, typeId, data } = this.editingType;

      if (mode === 'add') {
        await this._hass.callWS({
          type: 'ha_health_record/add_record_type',
          member_id: memberId,
          name: data.name,
          unit: data.unit,
          default_value: data.default_value,
        });
      } else {
        await this._hass.callWS({
          type: 'ha_health_record/update_record_type',
          member_id: memberId,
          type_id: typeId,
          name: data.name,
          unit: data.unit,
          default_value: data.default_value,
        });
      }

      this._closeTypeDialog();
      // Wait for integration reload to complete before fetching data
      await this._waitForReloadAndRefresh();
    } catch (error) {
      console.error('Error saving type:', error);
      alert('Failed to save type: ' + error.message);
    }

    this.submitting = false;
    this._render();
  }

  // Helper to wait for integration reload and refresh data
  async _waitForReloadAndRefresh() {
    // The backend reloads the config entry which takes some time
    // Save current URL and tab state before reload
    const currentTab = this.activeTab;
    const currentSettingsSubTab = this.settingsSubTab;
    const panelUrl = '/ha-health-record';

    // Wait a bit then try to reload data, with retries
    const maxRetries = 10;
    const retryDelay = 300; // ms

    for (let i = 0; i < maxRetries; i++) {
      await new Promise(resolve => setTimeout(resolve, retryDelay));

      // Check if we've been navigated away
      if (window.location.pathname !== panelUrl) {
        console.log('Navigated away during reload, returning to panel...');
        // Use history API to navigate back to the panel
        history.pushState(null, '', panelUrl);
        // Dispatch a popstate event to trigger HA's router
        window.dispatchEvent(new PopStateEvent('popstate', { state: null }));
        await new Promise(resolve => setTimeout(resolve, 500));
      }

      try {
        await this._loadData();
        // Restore tab state
        this.activeTab = currentTab;
        this.settingsSubTab = currentSettingsSubTab;
        this._render();
        return; // Success
      } catch (error) {
        console.log(`Retry ${i + 1}/${maxRetries} failed, waiting...`);
        if (i === maxRetries - 1) {
          console.error('Failed to reload data after integration reload:', error);
        }
      }
    }
  }

  _showDeleteTypeConfirm(memberId, typeData) {
    this.deleteTarget = {
      type: 'recordType',
      id: typeData.type,
      name: typeData.name,
      memberId: memberId,
    };
    this.showDeleteConfirm = true;
    this._render();
  }

  // ============================================================================
  // Member Management
  // ============================================================================

  _openAddMemberDialog() {
    this.editingMember = {
      mode: 'add',
      data: { name: '', member_id: '', note: '' },
    };
    this.showMemberDialog = true;
    this._render();
  }

  _openEditMemberDialog(member) {
    this.editingMember = {
      mode: 'edit',
      originalId: member.id,
      data: { name: member.name, member_id: member.id, note: member.note || '' },
    };
    this.showMemberDialog = true;
    this._render();
  }

  _closeMemberDialog() {
    this.showMemberDialog = false;
    this.editingMember = null;
    this._render();
  }

  async _saveMember() {
    if (this.submitting || !this.editingMember) return;
    this.submitting = true;
    this._render();

    try {
      const { mode, originalId, data } = this.editingMember;

      if (mode === 'add') {
        await this._hass.callWS({
          type: 'ha_health_record/add_member',
          name: data.name,
          ...(data.member_id ? { member_id: data.member_id } : {}),
          ...(data.note ? { note: data.note } : {}),
        });
      } else {
        await this._hass.callWS({
          type: 'ha_health_record/update_member',
          member_id: originalId,
          name: data.name,
          ...(data.note !== undefined ? { note: data.note } : {}),
        });
      }

      this._closeMemberDialog();
      // Wait for integration reload to complete before fetching data
      await this._waitForReloadAndRefresh();
    } catch (error) {
      console.error('Error saving member:', error);
      alert('Failed to save member: ' + error.message);
    }

    this.submitting = false;
    this._render();
  }

  _showDeleteMemberConfirm(member) {
    this.deleteTarget = {
      type: 'member',
      id: member.id,
      name: member.name,
    };
    this.showDeleteConfirm = true;
    this._render();
  }

  // ============================================================================
  // Delete Confirmation
  // ============================================================================

  _closeDeleteConfirm() {
    this.showDeleteConfirm = false;
    this.deleteTarget = null;
    this._render();
  }

  async _confirmDelete() {
    if (this.submitting || !this.deleteTarget) return;
    this.submitting = true;
    this._render();

    try {
      const { type, id, memberId, record } = this.deleteTarget;
      let needsReloadWait = false;

      switch (type) {
        case 'record':
          await this._hass.callWS({
            type: 'ha_health_record/delete_record',
            member_id: record.member_id,
            type_id: record.record_type,
            timestamp: record.timestamp,
            ...(record.id ? { record_id: record.id } : {}),
          });
          break;
        case 'recordType':
          await this._hass.callWS({
            type: 'ha_health_record/delete_record_type',
            member_id: memberId,
            type_id: id,
          });
          needsReloadWait = true;
          break;
        case 'member':
          await this._hass.callWS({
            type: 'ha_health_record/delete_member',
            member_id: id,
          });
          needsReloadWait = true;
          // Reset selected member if deleted
          if (this.selectedMemberId === id) {
            this.selectedMemberId = '';
          }
          break;
      }

      this._closeDeleteConfirm();
      this.expandedRecordId = null;
      this.editingRecord = null;

      // Wait for integration reload if needed
      if (needsReloadWait) {
        await this._waitForReloadAndRefresh();
      } else {
        await this._loadData();
      }
    } catch (error) {
      console.error('Error deleting:', error);
      alert('Failed to delete: ' + error.message);
    }

    this.submitting = false;
    this._render();
  }

  // ============================================================================
  // Render
  // ============================================================================

  _render() {
    const styles = `
      :host {
        display: block;
        padding: 16px;
        background: var(--primary-background-color, #fafafa);
        min-height: 100vh;
        font-family: var(--paper-font-body1_-_font-family, Roboto, sans-serif);
      }

      /* TOP BAR */
      .top-bar {
        display: flex;
        align-items: center;
        height: 56px;
        padding: 0 16px;
        background: var(--app-header-background-color, var(--primary-background-color));
        color: var(--app-header-text-color, var(--primary-text-color));
        border-bottom: 1px solid var(--divider-color);
        position: sticky;
        top: 0;
        z-index: 100;
        gap: 12px;
        margin: -16px -16px 16px -16px;
      }
      .top-bar-sidebar-btn {
        width: 40px;
        height: 40px;
        border: none;
        background: transparent;
        color: inherit;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 50%;
        transition: background 0.2s;
        flex-shrink: 0;
      }
      .top-bar-sidebar-btn:hover { background: var(--secondary-background-color, rgba(0, 0, 0, 0.1)); }
      .top-bar-sidebar-btn svg { width: 24px; height: 24px; }
      .top-bar-title {
        flex: 1;
        font-size: 20px;
        font-weight: 500;
        margin: 0;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        color: inherit;
      }
      .top-bar-actions { display: flex; align-items: center; gap: 4px; flex-shrink: 0; }

      /* SEARCH ROW */
      .search-row {
        display: flex;
        align-items: center;
        height: 48px;
        padding: 0 16px;
        background: var(--primary-background-color);
        border-bottom: 1px solid var(--divider-color);
        margin: 0 -16px 16px -16px;
        gap: 8px;
      }
      .search-row-input-wrapper {
        flex: 1;
        display: flex;
        align-items: center;
        background: var(--card-background-color);
        border: 1px solid var(--divider-color);
        border-radius: 8px;
        padding: 0 12px;
        height: 36px;
        transition: border-color 0.2s, box-shadow 0.2s;
      }
      .search-row-input-wrapper:focus-within {
        border-color: var(--primary-color);
        box-shadow: 0 0 0 2px rgba(var(--rgb-primary-color, 3, 169, 244), 0.2);
      }
      .search-row-icon {
        width: 20px;
        height: 20px;
        color: var(--secondary-text-color);
        flex-shrink: 0;
        margin-right: 8px;
      }
      .search-row-input {
        flex: 1;
        border: none;
        background: transparent;
        font-size: 14px;
        color: var(--primary-text-color);
        outline: none;
        height: 100%;
      }
      .search-row-input::placeholder { color: var(--secondary-text-color); }

      /* TIME FILTER ROW */
      .time-filter-row {
        display: flex;
        align-items: center;
        gap: 8px;
        padding: 0 16px;
        margin: 0 -16px 16px -16px;
        flex-wrap: wrap;
      }
      .time-filter-row input {
        padding: 8px 12px;
        border: 1px solid var(--divider-color);
        border-radius: 8px;
        background: var(--card-background-color);
        color: var(--primary-text-color);
        font-size: 14px;
      }
      .time-filter-row span {
        color: var(--secondary-text-color);
      }
      .filter-btn {
        padding: 8px 16px;
        background: var(--primary-color);
        color: white;
        border: none;
        border-radius: 8px;
        cursor: pointer;
        font-size: 14px;
        transition: opacity 0.2s;
      }
      .filter-btn:hover { opacity: 0.9; }

      /* MEMBER SWITCHER - Chip-style cards */
      .member-switcher-row {
        display: flex;
        align-items: center;
        padding: 0 16px 16px 16px;
        gap: 12px;
        flex-wrap: wrap;
        margin: 0 -16px;
      }
      .member-chip {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 12px 16px;
        background: var(--card-background-color);
        border-radius: 12px;
        cursor: pointer;
        transition: all 0.2s;
        border: 2px solid transparent;
        box-shadow: var(--ha-card-box-shadow, 0 2px 2px rgba(0,0,0,0.1));
        min-width: 140px;
      }
      .member-chip:hover {
        box-shadow: 0 4px 8px rgba(0,0,0,0.15);
        transform: translateY(-2px);
      }
      .member-chip.active {
        border-color: var(--primary-color);
        background: var(--primary-color);
      }
      .member-chip.active .member-chip-name,
      .member-chip.active .member-chip-stat {
        color: var(--text-primary-color, white);
      }
      .member-chip-avatar {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        background: var(--primary-color);
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-size: 18px;
        font-weight: 500;
        flex-shrink: 0;
      }
      .member-chip.active .member-chip-avatar {
        background: rgba(255,255,255,0.2);
      }
      .member-chip-info {
        display: flex;
        flex-direction: column;
        gap: 2px;
      }
      .member-chip-name {
        font-size: 14px;
        font-weight: 500;
        color: var(--primary-text-color);
      }
      .member-chip-stat {
        font-size: 12px;
        color: var(--secondary-text-color);
      }
      .member-chip-add {
        display: flex;
        align-items: center;
        gap: 8px;
        padding: 12px 16px;
        background: transparent;
        border-radius: 12px;
        cursor: pointer;
        transition: all 0.2s;
        border: 2px dashed var(--divider-color, #ccc);
        min-width: 120px;
        justify-content: center;
      }
      .member-chip-add:hover {
        border-color: var(--primary-color);
        background: var(--secondary-background-color, #f5f5f5);
      }
      .member-chip-add-icon {
        font-size: 20px;
        color: var(--secondary-text-color, #757575);
      }
      .member-chip-add-label {
        font-size: 14px;
        color: var(--secondary-text-color, #757575);
      }
      .member-chip-add:hover .member-chip-add-icon,
      .member-chip-add:hover .member-chip-add-label {
        color: var(--primary-color);
      }

      /* MEMBER OVERVIEW CARD */
      .overview-card {
        background: var(--card-background-color);
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 16px;
        box-shadow: var(--ha-card-box-shadow, 0 2px 2px rgba(0,0,0,0.1));
      }
      .overview-card-stat-label {
        font-size: 14px;
        color: var(--secondary-text-color);
        margin-bottom: 4px;
      }
      .overview-card-stat-primary {
        font-size: 32px;
        font-weight: bold;
        color: var(--primary-text-color);
      }
      .overview-card-details {
        font-size: 14px;
        color: var(--secondary-text-color);
        margin-top: 8px;
      }
      .overview-stats-row {
        display: flex;
        gap: 24px;
        margin-top: 12px;
        flex-wrap: wrap;
      }
      .overview-stat-item {
        display: flex;
        flex-direction: column;
        gap: 2px;
      }
      .overview-stat-value {
        font-size: 18px;
        font-weight: 600;
        color: var(--primary-text-color);
      }
      .overview-stat-label {
        font-size: 12px;
        color: var(--secondary-text-color);
      }

      /* Tab Navigation */
      .tabs {
        display: flex;
        gap: 0;
        margin-bottom: 16px;
        border-bottom: 2px solid var(--divider-color, #e0e0e0);
      }
      .tab {
        padding: 12px 24px;
        background: transparent;
        border: none;
        cursor: pointer;
        font-size: 14px;
        font-weight: 500;
        color: var(--secondary-text-color, #757575);
        border-bottom: 2px solid transparent;
        margin-bottom: -2px;
        transition: color 0.2s, border-color 0.2s;
      }
      .tab:hover {
        color: var(--primary-text-color, #212121);
      }
      .tab.active {
        color: var(--primary-color, #03a9f4);
        border-bottom-color: var(--primary-color, #03a9f4);
      }

      /* Sub-tabs */
      .sub-tabs {
        display: flex;
        gap: 8px;
        margin-bottom: 16px;
      }
      .sub-tab {
        padding: 8px 16px;
        background: var(--secondary-background-color, #e0e0e0);
        border: none;
        border-radius: 20px;
        cursor: pointer;
        font-size: 13px;
        color: var(--primary-text-color, #212121);
        transition: background 0.2s;
      }
      .sub-tab:hover {
        background: var(--divider-color, #bdbdbd);
      }
      .sub-tab.active {
        background: var(--primary-color, #03a9f4);
        color: white;
      }

      .members-section {
        display: flex;
        gap: 16px;
        margin-bottom: 24px;
        flex-wrap: wrap;
      }
      .member-card {
        background: var(--card-background-color, white);
        border-radius: 12px;
        padding: 16px;
        min-width: 200px;
        box-shadow: 0 2px 2px rgba(0, 0, 0, 0.1);
      }
      .member-card h3 {
        margin: 0 0 12px 0;
        color: var(--primary-text-color, #212121);
        font-size: 18px;
      }
      .quick-actions {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        margin-top: 12px;
      }
      .quick-actions button {
        padding: 6px 12px;
        background: var(--primary-color, #03a9f4);
        color: white;
        border: none;
        border-radius: 16px;
        cursor: pointer;
        font-size: 12px;
        transition: opacity 0.2s;
      }
      .quick-actions button:hover {
        opacity: 0.9;
      }
      .timeline-section {
        background: var(--card-background-color, white);
        border-radius: 12px;
        padding: 16px;
        box-shadow: 0 2px 2px rgba(0, 0, 0, 0.1);
      }
      .timeline-section h2 {
        margin: 0 0 16px 0;
        font-size: 18px;
        color: var(--primary-text-color, #212121);
      }
      .timeline-item {
        padding: 12px;
        border-bottom: 1px solid var(--divider-color, #e0e0e0);
        cursor: pointer;
        transition: background 0.2s;
      }
      .timeline-item:hover {
        background: var(--secondary-background-color, #f5f5f5);
      }
      .timeline-item:last-child {
        border-bottom: none;
      }
      .timeline-item.expanded {
        background: var(--secondary-background-color, #f5f5f5);
      }
      .timeline-row {
        display: flex;
        gap: 12px;
        align-items: flex-start;
      }
      .timeline-time {
        min-width: 60px;
        color: var(--secondary-text-color, #757575);
        font-size: 14px;
      }
      .timeline-content {
        flex: 1;
      }
      .timeline-member {
        font-weight: 500;
        color: var(--primary-text-color, #212121);
      }
      .timeline-activity {
        color: var(--secondary-text-color, #757575);
        font-size: 14px;
      }

      /* Expanded edit form */
      .timeline-edit-form {
        margin-top: 12px;
        padding: 12px;
        background: var(--card-background-color, white);
        border-radius: 8px;
        border: 1px solid var(--divider-color, #e0e0e0);
      }
      .edit-field {
        margin-bottom: 12px;
      }
      .edit-field label {
        display: block;
        margin-bottom: 4px;
        font-size: 12px;
        color: var(--secondary-text-color, #757575);
      }
      .edit-field input {
        width: 100%;
        padding: 8px;
        border: 1px solid var(--divider-color, #e0e0e0);
        border-radius: 4px;
        box-sizing: border-box;
        background: var(--card-background-color);
        color: var(--primary-text-color);
      }
      .edit-actions {
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: 8px;
      }
      .edit-actions-left {
        display: flex;
        gap: 8px;
      }

      /* Manage Tab Styles */
      .manage-section {
        background: var(--card-background-color, white);
        border-radius: 12px;
        padding: 16px;
        box-shadow: 0 2px 2px rgba(0, 0, 0, 0.1);
      }
      .type-card {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 12px;
        border: 1px solid var(--divider-color, #e0e0e0);
        border-radius: 8px;
        margin-bottom: 8px;
      }
      .type-info {
        flex: 1;
      }
      .type-name {
        font-weight: 500;
        color: var(--primary-text-color, #212121);
      }
      .type-details {
        font-size: 13px;
        color: var(--secondary-text-color, #757575);
        margin-top: 4px;
      }
      .type-actions {
        display: flex;
        gap: 8px;
      }
      .member-label {
        font-size: 12px;
        color: var(--secondary-text-color, #757575);
        margin-bottom: 8px;
        padding-top: 16px;
      }
      .member-label:first-child {
        padding-top: 0;
      }
      .add-button {
        display: block;
        width: 100%;
        padding: 12px;
        margin-top: 16px;
        background: var(--primary-color, #03a9f4);
        color: white;
        border: none;
        border-radius: 8px;
        cursor: pointer;
        font-size: 14px;
        font-weight: 500;
      }
      .add-button:hover {
        opacity: 0.9;
      }

      /* Dialogs */
      .dialog-overlay {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0, 0, 0, 0.5);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 1000;
      }
      .dialog {
        background: var(--card-background-color, white);
        border-radius: 12px;
        padding: 24px;
        min-width: 320px;
        max-width: 90vw;
      }
      .dialog h3 {
        margin: 0 0 16px 0;
        color: var(--primary-text-color, #212121);
      }
      .dialog-field {
        margin-bottom: 16px;
      }
      .dialog-field label {
        display: block;
        margin-bottom: 4px;
        color: var(--secondary-text-color, #757575);
        font-size: 13px;
      }
      .dialog-field input, .dialog-field select, .dialog-field textarea {
        width: 100%;
        padding: 8px;
        border: 1px solid var(--divider-color, #e0e0e0);
        border-radius: 4px;
        box-sizing: border-box;
        background: var(--card-background-color, white);
        color: var(--primary-text-color, #212121);
        font-family: inherit;
      }
      .dialog-field textarea {
        min-height: 60px;
        resize: vertical;
      }
      .dialog-actions {
        display: flex;
        justify-content: flex-end;
        gap: 8px;
        margin-top: 20px;
      }
      .btn {
        padding: 8px 16px;
        border: none;
        border-radius: 4px;
        cursor: pointer;
        font-size: 14px;
      }
      .btn-primary {
        background: var(--primary-color, #03a9f4);
        color: white;
      }
      .btn-secondary {
        background: var(--secondary-background-color, #e0e0e0);
        color: var(--primary-text-color, #212121);
      }
      .btn-danger {
        background: #f44336;
        color: white;
      }
      .btn-icon {
        padding: 6px 10px;
        background: transparent;
        border: 1px solid var(--divider-color, #e0e0e0);
        border-radius: 4px;
        cursor: pointer;
        font-size: 14px;
      }
      .btn-icon:hover {
        background: var(--secondary-background-color, #f5f5f5);
      }
      .btn-icon.danger {
        color: #f44336;
        border-color: #f44336;
      }
      .btn:disabled {
        opacity: 0.6;
        cursor: not-allowed;
      }
      .loading {
        text-align: center;
        padding: 40px;
        color: var(--secondary-text-color, #757575);
      }
      .empty {
        text-align: center;
        padding: 40px;
        color: var(--secondary-text-color, #757575);
      }

      /* Delete Confirm Dialog */
      .delete-confirm-text {
        color: var(--primary-text-color, #212121);
        margin-bottom: 20px;
      }

      /* Timestamp row */
      .timestamp-row {
        display: flex;
        gap: 8px;
        align-items: center;
      }
      .timestamp-row input {
        flex: 1;
      }
      .btn-small {
        padding: 6px 12px;
        font-size: 12px;
      }

      /* Type records (records under type cards) */
      .type-records {
        margin-left: 16px;
        margin-bottom: 16px;
        border-left: 2px solid var(--divider-color, #e0e0e0);
        padding-left: 12px;
      }
      .record-item {
        padding: 8px;
        margin-bottom: 4px;
        background: var(--secondary-background-color, #f5f5f5);
        border-radius: 4px;
        cursor: pointer;
        transition: background 0.2s;
      }
      .record-item:hover {
        background: var(--divider-color, #e0e0e0);
      }
      .record-item.expanded {
        background: var(--card-background-color, white);
        border: 1px solid var(--divider-color, #e0e0e0);
      }
      .record-row {
        display: flex;
        gap: 12px;
        align-items: center;
        flex-wrap: wrap;
      }
      .record-time {
        font-size: 13px;
        color: var(--secondary-text-color, #757575);
        min-width: 120px;
      }
      .record-value {
        font-weight: 500;
        color: var(--primary-text-color, #212121);
      }
      .record-note {
        font-size: 13px;
        color: var(--secondary-text-color, #757575);
        font-style: italic;
      }

      /* Mobile responsive */
      @media (max-width: 600px) {
        :host {
          padding: 8px;
        }
        .top-bar {
          margin: -8px -8px 8px -8px;
        }
        .search-row {
          margin: 0 -8px 8px -8px;
          flex-wrap: wrap;
          height: auto;
          padding: 8px;
        }
        .time-filter-row {
          margin: 0 -8px 8px -8px;
          padding: 8px;
        }
        .member-switcher-row {
          padding: 0 8px 16px 8px;
          overflow-x: auto;
          flex-wrap: nowrap;
          -webkit-overflow-scrolling: touch;
          margin: 0 -8px;
        }
        .member-chip {
          min-width: 130px;
          flex-shrink: 0;
          padding: 10px 14px;
        }
        .member-chip-avatar {
          width: 36px;
          height: 36px;
          font-size: 16px;
        }
        .overview-card {
          padding: 12px;
        }
        .overview-card-stat-primary {
          font-size: 28px;
        }
      }
    `;

    let content = '';

    if (this.loading) {
      content = `<div class="loading">${this._t('loading')}</div>`;
    } else {
      // Top Bar (like Finance Record)
      content = `
        <div class="top-bar">
          <button class="top-bar-sidebar-btn" id="sidebar-btn" title="${this._t('menu')}">
            <svg viewBox="0 0 24 24"><path fill="currentColor" d="M3,6H21V8H3V6M3,11H21V13H3V11M3,16H21V18H3V16Z"/></svg>
          </button>
          <h1 class="top-bar-title">${this._t('title')}</h1>
        </div>
      `;

      // Member Switcher Chips (always visible above tabs)
      if (this.members.length > 0) {
        content += this._renderMemberSwitcher();
        // Member Overview Card
        const selectedMemberOverview = this.members.find(m => m.id === this.selectedMemberId);
        if (selectedMemberOverview) {
          content += this._renderOverviewCard(selectedMemberOverview);
        }
      }

      // Tab Navigation
      content += `
        <div class="tabs">
          <button class="tab ${this.activeTab === 'record' ? 'active' : ''}" data-tab="record">${this._t('record')}</button>
          <button class="tab ${this.activeTab === 'settings' ? 'active' : ''}" data-tab="settings">${this._t('settings')}</button>
        </div>
      `;

      if (this.activeTab === 'record') {
        content += this._renderRecordTab();
      } else {
        content += this._renderSettingsTab();
      }
    }

    // Dialogs
    content += this._renderDialogs();

    this.shadowRoot.innerHTML = `<style>${styles}</style>${content}`;

    // Attach event listeners
    this._attachEventListeners();
  }

  _renderMemberSwitcher() {
    let html = '<div class="member-switcher-row">';
    for (const member of this.members) {
      const isActive = member.id === this.selectedMemberId;
      const initial = (member.name || '?').charAt(0).toUpperCase();
      const typeCount = (member.record_sets || []).length;
      html += `
        <div class="member-chip ${isActive ? 'active' : ''}" data-member-id="${member.id}">
          <div class="member-chip-avatar">${initial}</div>
          <div class="member-chip-info">
            <div class="member-chip-name">${this._escapeHtml(member.name)}</div>
            <div class="member-chip-stat">${typeCount} ${this._t('recordTypes')}</div>
          </div>
        </div>
      `;
    }
    html += `
      <div class="member-chip-add" id="add-member-chip">
        <span class="member-chip-add-icon">+</span>
        <span class="member-chip-add-label">${this._t('addMember')}</span>
      </div>
    `;
    html += '</div>';
    return html;
  }

  _renderOverviewCard(member) {
    // Count records for this member in current date range
    const memberRecords = this.records.filter(r => r.member_id === member.id);
    const totalCount = memberRecords.length;

    // Find last record
    let lastRecordInfo = this._t('noRecordsYet');
    if (memberRecords.length > 0) {
      const sorted = [...memberRecords].sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
      const last = sorted[0];
      const typeName = last.record_name || last.record_type || '';
      lastRecordInfo = `${this._formatDate(last.timestamp)} ${this._formatTime(last.timestamp)} - ${this._escapeHtml(typeName)}`;
    }

    const typeCount = (member.record_sets || []).length;

    return `
      <div class="overview-card">
        <div class="overview-card-stat-label">${this._t('totalRecords')}</div>
        <div class="overview-card-stat-primary">${totalCount}</div>
        <div class="overview-card-details">${this._t('lastRecord')}: ${lastRecordInfo}</div>
        <div class="overview-stats-row">
          <div class="overview-stat-item">
            <div class="overview-stat-value">${typeCount}</div>
            <div class="overview-stat-label">${this._t('recordTypesCount')}</div>
          </div>
        </div>
      </div>
    `;
  }

  _renderRecordTab() {
    let html = '';

    // Search Row
    html += `
      <div class="search-row">
        <div class="search-row-input-wrapper">
          <svg class="search-row-icon" viewBox="0 0 24 24"><path fill="currentColor" d="M9.5,3A6.5,6.5 0 0,1 16,9.5C16,11.11 15.41,12.59 14.44,13.73L14.71,14H15.5L20.5,19L19,20.5L14,15.5V14.71L13.73,14.44C12.59,15.41 11.11,16 9.5,16A6.5,6.5 0 0,1 3,9.5A6.5,6.5 0 0,1 9.5,3M9.5,5C7,5 5,7 5,9.5C5,12 7,14 9.5,14C12,14 14,12 14,9.5C14,7 12,5 9.5,5Z"/></svg>
          <input
            class="search-row-input"
            type="text"
            id="search-input"
            placeholder="${this._t('search')}"
            value="${this._escapeHtml(this.searchQuery)}"
          />
        </div>
      </div>
    `;

    // Time Filter Row
    html += `
      <div class="time-filter-row">
        <input type="datetime-local" id="start-date" value="${this.startDate}">
        <span>${this._t('to')}</span>
        <input type="datetime-local" id="end-date" value="${this.endDate}">
        <button class="filter-btn" id="filter-btn">${this._t('filter')}</button>
      </div>
    `;

    // Quick action buttons for selected member (all record types as buttons, no category split)
    const selectedMember = this.members.find(m => m.id === this.selectedMemberId);
    if (selectedMember) {
      const memberJson = JSON.stringify(selectedMember).replace(/'/g, "&#39;").replace(/"/g, '&quot;');
      const sets = selectedMember.record_sets || [];

      if (sets.length > 0) {
        html += `
          <div class="member-card" style="width: 100%; box-sizing: border-box;">
            <h3>${this._escapeHtml(selectedMember.name)}</h3>
            <div class="quick-actions">
        `;

        for (const recordSet of sets) {
          html += `
            <button class="quick-action-btn" data-member='${memberJson}' data-type="${recordSet.type}">
              ${this._escapeHtml(recordSet.name || recordSet.type)}
            </button>
          `;
        }

        html += '</div></div>';
      } else {
        html += `<div class="empty">${this._t('noRecordTypes')}</div>`;
      }
    } else if (this.members.length === 0) {
      html += `<div class="empty">${this._t('noMembers')}</div>`;
    }

    // Records timeline section (unified, no sub-tabs)
    const filteredRecords = this._getFilteredRecords();
    html += `<div class="timeline-section"><h2>${this._t('record')}</h2>`;
    if (filteredRecords.length === 0) {
      html += `<div class="empty">${this._t('noRecords')}</div>`;
    } else {
      for (const record of filteredRecords) {
        const recordId = this._generateRecordId(record);
        const isExpanded = this.expandedRecordId === recordId;
        const recordJson = JSON.stringify(record).replace(/'/g, "&#39;").replace(/"/g, '&quot;');

        html += `
          <div class="timeline-item ${isExpanded ? 'expanded' : ''}" data-record='${recordJson}'>
            <div class="timeline-row">
              <div class="timeline-time">${this._formatTime(record.timestamp)}</div>
              <div class="timeline-content">
                <div class="timeline-member">${this._escapeHtml(record.member_name)}</div>
                <div class="timeline-activity">
                  ${this._escapeHtml(record.record_name || record.record_type)}:
                  ${record.value != null ? record.value : ''}
                  ${record.unit ? this._escapeHtml(record.unit) : ''}
                  ${record.note ? ` - "${this._escapeHtml(record.note)}"` : ''}
                </div>
              </div>
            </div>
        `;

        if (isExpanded && this.editingRecord) {
          html += `
            <div class="timeline-edit-form">
              <div class="edit-field">
                <label>${this._t('timestamp')}</label>
                <div class="timestamp-row">
                  <input type="datetime-local" id="edit-timestamp" value="${this.editingRecord.timestamp}">
                  <button class="btn btn-secondary btn-small" id="edit-now-btn">${this._t('now')}</button>
                </div>
              </div>
              <div class="edit-field">
                <label>${this._t('value')}${record.unit ? ` (${record.unit})` : ''}</label>
                <input type="number" id="edit-value" value="${this.editingRecord.value}" step="0.1">
              </div>
              <div class="edit-field">
                <label>${this._t('note')}</label>
                <input type="text" id="edit-note" value="${this._escapeHtml(this.editingRecord.note)}" placeholder="${this._t('optionalNote')}">
              </div>
              <div class="edit-actions">
                <button class="btn-icon danger delete-record-btn" data-record='${recordJson}'>🗑 ${this._t('delete')}</button>
                <div class="edit-actions-left">
                  <button class="btn btn-secondary cancel-edit-btn">${this._t('cancel')}</button>
                  <button class="btn btn-primary save-edit-btn" data-record='${recordJson}' ${this.submitting ? 'disabled' : ''}>
                    ${this.submitting ? this._t('saving') : this._t('save')}
                  </button>
                </div>
              </div>
            </div>
          `;
        }

        html += '</div>';
      }
    }
    html += '</div>';

    return html;
  }

  _renderSettingsTab() {
    let html = '';

    // Settings sub-tabs: Members | Record Types
    html += `
      <div class="sub-tabs">
        <button class="sub-tab ${this.settingsSubTab === 'members' ? 'active' : ''}" data-settings-subtab="members">${this._t('members')}</button>
        <button class="sub-tab ${this.settingsSubTab === 'recordTypes' ? 'active' : ''}" data-settings-subtab="recordTypes">${this._t('recordTypes')}</button>
      </div>
    `;

    html += '<div class="manage-section">';

    if (this.settingsSubTab === 'members') {
      html += this._renderMembersManagement();
    } else {
      html += this._renderRecordTypesManagement();
    }

    html += '</div>';
    return html;
  }

  _renderRecordTypesManagement() {
    let html = '';

    const selectedMember = this.members.find(m => m.id === this.selectedMemberId);

    if (!selectedMember) {
      if (this.members.length === 0) {
        html += `<div class="empty">${this._t('noMembersManage')}</div>`;
      } else {
        html += `<div class="empty">${this._t('selectMember')}</div>`;
      }
    } else {
      html += `<div class="member-label">${this._t('member')}: ${this._escapeHtml(selectedMember.name)}</div>`;

      const recordSets = selectedMember.record_sets || [];
      if (recordSets.length === 0) {
        html += `<div class="empty" style="padding: 16px;">${this._t('noRecordTypes')}</div>`;
      } else {
        for (const recordSet of recordSets) {
          const typeJson = JSON.stringify(recordSet).replace(/'/g, "&#39;").replace(/"/g, '&quot;');
          html += `
            <div class="type-card">
              <div class="type-info">
                <div class="type-name">${this._escapeHtml(recordSet.name)}</div>
                <div class="type-details">${this._t('unit')}: ${this._escapeHtml(recordSet.unit)} | ${this._t('current')}: ${recordSet.current_value || 0}</div>
              </div>
              <div class="type-actions">
                <button class="btn-icon edit-type-btn" data-member="${selectedMember.id}" data-type='${typeJson}'>✏️</button>
                <button class="btn-icon danger delete-type-btn" data-member="${selectedMember.id}" data-type='${typeJson}'>🗑</button>
              </div>
            </div>
          `;
        }
      }
      html += `<button class="add-button" id="add-record-type-btn">${this._t('addRecordType')}</button>`;
    }

    return html;
  }

  _renderMembersManagement() {
    let html = '';
    const member = this.members.find(m => m.id === this.selectedMemberId);

    if (!member) {
      html += `<div class="empty">${this._t('noMembersYet')}</div>`;
    } else {
      const memberJson = JSON.stringify(member).replace(/'/g, "&#39;").replace(/"/g, '&quot;');
      html += `
        <div class="type-card">
          <div class="type-info">
            <div class="type-name">${this._escapeHtml(member.name)}</div>
            <div class="type-details">
              ID: ${this._escapeHtml(member.id)} | ${this._t('recordTypes')}: ${(member.record_sets || []).length}
              ${member.note ? `<br>${this._t('note')}: ${this._escapeHtml(member.note)}` : ''}
            </div>
          </div>
          <div class="type-actions">
            <button class="btn-icon edit-member-btn" data-member='${memberJson}'>✏️</button>
            <button class="btn-icon danger delete-member-btn" data-member='${memberJson}'>🗑</button>
          </div>
        </div>
      `;
    }

    return html;
  }

  _renderDialogs() {
    let html = '';

    // Input Dialog (Quick Log - unified for all record types)
    if (this.showInputDialog && this.selectedMember) {
      const typeInfo = (this.selectedMember.record_sets || []).find(s => s.type === this.selectedType);
      const dialogTitle = this._t('logFor', { type: this._escapeHtml(typeInfo?.name || this.selectedType), name: this._escapeHtml(this.selectedMember.name) });
      html += `
        <div class="dialog-overlay" id="input-dialog-overlay">
          <div class="dialog">
            <h3>${dialogTitle}</h3>
            <div class="dialog-field">
              <label>${this._t('timestamp')}</label>
              <div class="timestamp-row">
                <input type="datetime-local" id="input-timestamp" value="${this.inputTimestamp}">
                <button class="btn btn-secondary btn-small" id="input-now-btn">${this._t('now')}</button>
              </div>
            </div>
            <div class="dialog-field">
              <label>${this._t('value')}${typeInfo?.unit ? ` (${typeInfo.unit})` : ''}</label>
              <input type="number" id="input-value" value="${this.inputValue}" step="0.1">
            </div>
            <div class="dialog-field">
              <label>${this._t('note')}</label>
              <input type="text" id="input-note" placeholder="${this._t('optionalNote')}" value="${this._escapeHtml(this.inputNote)}">
            </div>
            <div class="dialog-actions">
              <button class="btn btn-secondary" id="cancel-input-btn">${this._t('cancel')}</button>
              <button class="btn btn-primary" id="save-input-btn" ${this.submitting ? 'disabled' : ''}>
                ${this.submitting ? this._t('saving') : this._t('save')}
              </button>
            </div>
          </div>
        </div>
      `;
    }

    // Type Dialog (Add/Edit Record Type - unified)
    if (this.showTypeDialog && this.editingType) {
      const isAdd = this.editingType.mode === 'add';
      const dialogTitle = isAdd ? this._t('addRecordTypeTitle') : this._t('editRecordTypeTitle');

      html += `
        <div class="dialog-overlay" id="type-dialog-overlay">
          <div class="dialog">
            <h3>${dialogTitle}</h3>
            ${isAdd ? `
              <div class="dialog-field">
                <label>${this._t('member')}</label>
                <select id="type-member">
                  ${this.members.map(m => `<option value="${m.id}" ${m.id === this.editingType.memberId ? 'selected' : ''}>${this._escapeHtml(m.name)}</option>`).join('')}
                </select>
              </div>
            ` : ''}
            <div class="dialog-field">
              <label>${this._t('name')}</label>
              <input type="text" id="type-name" value="${this._escapeHtml(this.editingType.data.name)}" placeholder="${this._t('namePlaceholder')}">
            </div>
            <div class="dialog-field">
              <label>${this._t('unit')}</label>
              <input type="text" id="type-unit" value="${this._escapeHtml(this.editingType.data.unit)}" placeholder="${this._t('unitPlaceholder')}">
            </div>
            <div class="dialog-field">
              <label>${this._t('defaultValue')}</label>
              <input type="number" id="type-default" value="${this.editingType.data.default_value}" step="0.1">
            </div>
            <div class="dialog-actions">
              <button class="btn btn-secondary" id="cancel-type-btn">${this._t('cancel')}</button>
              <button class="btn btn-primary" id="save-type-btn" ${this.submitting ? 'disabled' : ''}>
                ${this.submitting ? this._t('saving') : this._t('save')}
              </button>
            </div>
          </div>
        </div>
      `;
    }

    // Member Dialog (Add/Edit Member) - now with note field
    if (this.showMemberDialog && this.editingMember) {
      const isAdd = this.editingMember.mode === 'add';
      const dialogTitle = isAdd ? this._t('addMemberTitle') : this._t('editMemberTitle');

      html += `
        <div class="dialog-overlay" id="member-dialog-overlay">
          <div class="dialog">
            <h3>${dialogTitle}</h3>
            <div class="dialog-field">
              <label>${this._t('name')}</label>
              <input type="text" id="member-name" value="${this._escapeHtml(this.editingMember.data.name)}" placeholder="${this._t('memberNamePlaceholder')}">
            </div>
            ${isAdd ? `
              <div class="dialog-field">
                <label>${this._t('memberIdLabel')}</label>
                <input type="text" id="member-id" value="${this._escapeHtml(this.editingMember.data.member_id)}" placeholder="${this._t('memberIdPlaceholder')}">
              </div>
            ` : ''}
            <div class="dialog-field">
              <label>${this._t('memberNoteLabel')}</label>
              <textarea id="member-note" placeholder="${this._t('memberNotePlaceholder')}">${this._escapeHtml(this.editingMember.data.note || '')}</textarea>
            </div>
            <div class="dialog-actions">
              <button class="btn btn-secondary" id="cancel-member-btn">${this._t('cancel')}</button>
              <button class="btn btn-primary" id="save-member-btn" ${this.submitting ? 'disabled' : ''}>
                ${this.submitting ? this._t('saving') : this._t('save')}
              </button>
            </div>
          </div>
        </div>
      `;
    }

    // Delete Confirmation Dialog
    if (this.showDeleteConfirm && this.deleteTarget) {
      html += `
        <div class="dialog-overlay" id="delete-dialog-overlay">
          <div class="dialog">
            <h3>${this._t('confirmDelete')}</h3>
            <div class="delete-confirm-text">
              ${this._t('confirmDeleteMessage', { name: this._escapeHtml(this.deleteTarget.name) })}
            </div>
            <div class="dialog-actions">
              <button class="btn btn-secondary" id="cancel-delete-btn">${this._t('cancel')}</button>
              <button class="btn btn-danger" id="confirm-delete-btn" ${this.submitting ? 'disabled' : ''}>
                ${this.submitting ? this._t('deleting') : this._t('delete')}
              </button>
            </div>
          </div>
        </div>
      `;
    }

    return html;
  }

  _attachEventListeners() {
    // Sidebar toggle
    const sidebarBtn = this.shadowRoot.querySelector('#sidebar-btn');
    if (sidebarBtn) {
      sidebarBtn.addEventListener('click', () => this._toggleSidebar());
    }

    // Tab navigation
    this.shadowRoot.querySelectorAll('.tab').forEach(tab => {
      tab.addEventListener('click', () => this._switchTab(tab.dataset.tab));
    });

    // Settings sub-tab navigation
    this.shadowRoot.querySelectorAll('.sub-tab[data-settings-subtab]').forEach(tab => {
      tab.addEventListener('click', () => this._switchSettingsSubTab(tab.dataset.settingsSubtab));
    });

    // Filter button
    const filterBtn = this.shadowRoot.querySelector('#filter-btn');
    if (filterBtn) {
      filterBtn.addEventListener('click', () => this._handleDateChange());
    }

    // Search input
    const searchInput = this.shadowRoot.querySelector('#search-input');
    if (searchInput) {
      searchInput.addEventListener('input', (e) => this._onSearchInput(e));
    }

    // Member chip click handlers
    this.shadowRoot.querySelectorAll('.member-chip').forEach(chip => {
      chip.addEventListener('click', () => {
        const memberId = chip.dataset.memberId;
        if (memberId) {
          this.selectedMemberId = memberId;
          this._render();
        }
      });
    });

    // Add Member chip in member switcher
    const addMemberChip = this.shadowRoot.querySelector('#add-member-chip');
    if (addMemberChip) {
      addMemberChip.addEventListener('click', () => this._openAddMemberDialog());
    }

    // Quick action buttons (unified - all record types)
    this.shadowRoot.querySelectorAll('.quick-action-btn').forEach(btn => {
      btn.addEventListener('click', (e) => {
        e.stopPropagation();
        const memberData = btn.getAttribute('data-member');
        const type = btn.getAttribute('data-type');
        if (memberData && type) {
          const member = JSON.parse(memberData.replace(/&quot;/g, '"'));
          this._openInputDialog(member, type);
        }
      });
    });

    // Timeline item click (expand/collapse)
    this.shadowRoot.querySelectorAll('.timeline-item').forEach(item => {
      item.addEventListener('click', (e) => {
        // Don't toggle if clicking on form elements
        if (e.target.closest('.timeline-edit-form')) return;

        const recordData = item.getAttribute('data-record');
        if (recordData) {
          const record = JSON.parse(recordData.replace(/&quot;/g, '"'));
          this._toggleRecordExpand(record);
        }
      });
    });

    // Record item click in Record tab (expand/collapse)
    this.shadowRoot.querySelectorAll('.record-item').forEach(item => {
      item.addEventListener('click', (e) => {
        // Don't toggle if clicking on form elements
        if (e.target.closest('.timeline-edit-form')) return;

        const recordData = item.getAttribute('data-record');
        if (recordData) {
          const record = JSON.parse(recordData.replace(/&quot;/g, '"'));
          this._toggleRecordExpand(record);
        }
      });
    });

    // Edit form save button
    this.shadowRoot.querySelectorAll('.save-edit-btn').forEach(btn => {
      btn.addEventListener('click', (e) => {
        e.stopPropagation();
        const timestampInput = this.shadowRoot.querySelector('#edit-timestamp');
        const valueInput = this.shadowRoot.querySelector('#edit-value');
        const noteInput = this.shadowRoot.querySelector('#edit-note');
        if (timestampInput) this.editingRecord.timestamp = timestampInput.value;
        if (valueInput) this.editingRecord.value = parseFloat(valueInput.value) || 0;
        if (noteInput) this.editingRecord.note = noteInput.value;

        const recordData = btn.getAttribute('data-record');
        const record = JSON.parse(recordData.replace(/&quot;/g, '"'));
        this._saveRecordEdit(record);
      });
    });

    // Edit form "Now" button for timestamp
    const editNowBtn = this.shadowRoot.querySelector('#edit-now-btn');
    if (editNowBtn) {
      editNowBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        const newTimestamp = this._toLocalISOString(new Date());
        this.editingRecord.timestamp = newTimestamp;
        const timestampInput = this.shadowRoot.querySelector('#edit-timestamp');
        if (timestampInput) timestampInput.value = newTimestamp;
      });
    }

    // Edit form cancel button
    this.shadowRoot.querySelectorAll('.cancel-edit-btn').forEach(btn => {
      btn.addEventListener('click', (e) => {
        e.stopPropagation();
        this._cancelRecordEdit();
      });
    });

    // Delete record button
    this.shadowRoot.querySelectorAll('.delete-record-btn').forEach(btn => {
      btn.addEventListener('click', (e) => {
        e.stopPropagation();
        const recordData = btn.getAttribute('data-record');
        const record = JSON.parse(recordData.replace(/&quot;/g, '"'));
        this._showDeleteRecordConfirm(record);
      });
    });

    // Type management - Edit buttons
    this.shadowRoot.querySelectorAll('.edit-type-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        const memberId = btn.dataset.member;
        const typeData = JSON.parse(btn.dataset.type.replace(/&quot;/g, '"'));
        this._openEditTypeDialog(memberId, typeData);
      });
    });

    // Type management - Delete buttons
    this.shadowRoot.querySelectorAll('.delete-type-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        const memberId = btn.dataset.member;
        const typeData = JSON.parse(btn.dataset.type.replace(/&quot;/g, '"'));
        this._showDeleteTypeConfirm(memberId, typeData);
      });
    });

    // Type management - Add button
    const addRecordTypeBtn = this.shadowRoot.querySelector('#add-record-type-btn');
    if (addRecordTypeBtn) {
      addRecordTypeBtn.addEventListener('click', () => {
        this._openAddTypeDialog();
      });
    }

    // Member management - Edit buttons
    this.shadowRoot.querySelectorAll('.edit-member-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        const member = JSON.parse(btn.dataset.member.replace(/&quot;/g, '"'));
        this._openEditMemberDialog(member);
      });
    });

    // Member management - Delete buttons
    this.shadowRoot.querySelectorAll('.delete-member-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        const member = JSON.parse(btn.dataset.member.replace(/&quot;/g, '"'));
        this._showDeleteMemberConfirm(member);
      });
    });

    // Input Dialog buttons
    const cancelInputBtn = this.shadowRoot.querySelector('#cancel-input-btn');
    if (cancelInputBtn) {
      cancelInputBtn.addEventListener('click', () => this._closeInputDialog());
    }

    const saveInputBtn = this.shadowRoot.querySelector('#save-input-btn');
    if (saveInputBtn) {
      saveInputBtn.addEventListener('click', () => {
        const timestampInput = this.shadowRoot.querySelector('#input-timestamp');
        const valueInput = this.shadowRoot.querySelector('#input-value');
        const noteInput = this.shadowRoot.querySelector('#input-note');
        if (timestampInput) this.inputTimestamp = timestampInput.value;
        if (valueInput) this.inputValue = parseFloat(valueInput.value) || 0;
        if (noteInput) this.inputNote = noteInput.value;
        this._submitInput();
      });
    }

    const inputNowBtn = this.shadowRoot.querySelector('#input-now-btn');
    if (inputNowBtn) {
      inputNowBtn.addEventListener('click', () => {
        this.inputTimestamp = this._toLocalISOString(new Date());
        const timestampInput = this.shadowRoot.querySelector('#input-timestamp');
        if (timestampInput) timestampInput.value = this.inputTimestamp;
      });
    }

    const inputDialogOverlay = this.shadowRoot.querySelector('#input-dialog-overlay');
    if (inputDialogOverlay) {
      inputDialogOverlay.addEventListener('click', (e) => {
        if (e.target === inputDialogOverlay) this._closeInputDialog();
      });
    }

    // Type Dialog buttons
    const cancelTypeBtn = this.shadowRoot.querySelector('#cancel-type-btn');
    if (cancelTypeBtn) {
      cancelTypeBtn.addEventListener('click', () => this._closeTypeDialog());
    }

    const saveTypeBtn = this.shadowRoot.querySelector('#save-type-btn');
    if (saveTypeBtn) {
      saveTypeBtn.addEventListener('click', () => {
        const memberSelect = this.shadowRoot.querySelector('#type-member');
        const nameInput = this.shadowRoot.querySelector('#type-name');
        const unitInput = this.shadowRoot.querySelector('#type-unit');
        const defaultInput = this.shadowRoot.querySelector('#type-default');

        if (memberSelect) this.editingType.memberId = memberSelect.value;
        if (nameInput) this.editingType.data.name = nameInput.value;
        if (unitInput) this.editingType.data.unit = unitInput.value;
        if (defaultInput) this.editingType.data.default_value = parseFloat(defaultInput.value) || 0;

        this._saveType();
      });
    }

    const typeDialogOverlay = this.shadowRoot.querySelector('#type-dialog-overlay');
    if (typeDialogOverlay) {
      typeDialogOverlay.addEventListener('click', (e) => {
        if (e.target === typeDialogOverlay) this._closeTypeDialog();
      });
    }

    // Member Dialog buttons
    const cancelMemberBtn = this.shadowRoot.querySelector('#cancel-member-btn');
    if (cancelMemberBtn) {
      cancelMemberBtn.addEventListener('click', () => this._closeMemberDialog());
    }

    const saveMemberBtn = this.shadowRoot.querySelector('#save-member-btn');
    if (saveMemberBtn) {
      saveMemberBtn.addEventListener('click', () => {
        const nameInput = this.shadowRoot.querySelector('#member-name');
        const idInput = this.shadowRoot.querySelector('#member-id');
        const noteInput = this.shadowRoot.querySelector('#member-note');

        if (nameInput) this.editingMember.data.name = nameInput.value;
        if (idInput) this.editingMember.data.member_id = idInput.value;
        if (noteInput) this.editingMember.data.note = noteInput.value;

        this._saveMember();
      });
    }

    const memberDialogOverlay = this.shadowRoot.querySelector('#member-dialog-overlay');
    if (memberDialogOverlay) {
      memberDialogOverlay.addEventListener('click', (e) => {
        if (e.target === memberDialogOverlay) this._closeMemberDialog();
      });
    }

    // Delete Confirmation Dialog buttons
    const cancelDeleteBtn = this.shadowRoot.querySelector('#cancel-delete-btn');
    if (cancelDeleteBtn) {
      cancelDeleteBtn.addEventListener('click', () => this._closeDeleteConfirm());
    }

    const confirmDeleteBtn = this.shadowRoot.querySelector('#confirm-delete-btn');
    if (confirmDeleteBtn) {
      confirmDeleteBtn.addEventListener('click', () => this._confirmDelete());
    }

    const deleteDialogOverlay = this.shadowRoot.querySelector('#delete-dialog-overlay');
    if (deleteDialogOverlay) {
      deleteDialogOverlay.addEventListener('click', (e) => {
        if (e.target === deleteDialogOverlay) this._closeDeleteConfirm();
      });
    }
  }

  _escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }
}

customElements.define('ha-health-record-panel', HaHealthRecordPanel);
