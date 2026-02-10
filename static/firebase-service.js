// Firebase Service Functions

// Register user
async function registerUser(email, password, fullName, role = 'user') {
    try {
        const userCredential = await auth.createUserWithEmailAndPassword(email, password);
        await db.collection('users').doc(userCredential.user.uid).set({
            email: email,
            fullName: fullName,
            role: role,
            createdAt: firebase.firestore.FieldValue.serverTimestamp()
        });
        return { success: true, user: { id: userCredential.user.uid, email, fullName, role } };
    } catch (error) {
        return { success: false, error: error.message };
    }
}

// Login
async function loginUser(email, password) {
    try {
        const userCredential = await auth.signInWithEmailAndPassword(email, password);
        const userDoc = await db.collection('users').doc(userCredential.user.uid).get();
        let userData = { id: userCredential.user.uid, email: userCredential.user.email };
        if (userDoc.exists) userData = { ...userData, ...userDoc.data() };
        return { success: true, user: userData };
    } catch (error) {
        return { success: false, error: error.message };
    }
}

// Logout
async function logoutUser() {
    await auth.signOut();
}

// Get equipment
async function getEquipment() {
    const snapshot = await db.collection('equipment').orderBy('createdAt', 'desc').get();
    return snapshot.docs.map(doc => ({ id: doc.id, ...doc.data() }));
}

// Add equipment
async function addEquipment(data) {
    const docRef = await db.collection('equipment').add({
        ...data,
        status: 'available',
        createdAt: firebase.firestore.FieldValue.serverTimestamp()
    });
    return { success: true, id: docRef.id };
}

// Update equipment
async function updateEquipment(id, data) {
    await db.collection('equipment').doc(id).update({
        ...data,
        updatedAt: firebase.firestore.FieldValue.serverTimestamp()
    });
    return { success: true };
}

// Delete equipment
async function deleteEquipment(id) {
    await db.collection('equipment').doc(id).delete();
    return { success: true };
}

// Borrow equipment
async function borrowEquipment(equipmentId, userId) {
    await db.collection('equipment').doc(equipmentId).update({
        status: 'borrowed',
        borrowerId: userId,
        borrowedAt: firebase.firestore.FieldValue.serverTimestamp()
    });
    await db.collection('borrow_history').add({
        equipmentId,
        userId,
        action: 'borrow',
        timestamp: firebase.firestore.FieldValue.serverTimestamp()
    });
    return { success: true };
}

// Return equipment
async function returnEquipment(equipmentId, userId) {
    await db.collection('equipment').doc(equipmentId).update({
        status: 'available',
        borrowerId: null,
        returnedAt: firebase.firestore.FieldValue.serverTimestamp()
    });
    await db.collection('borrow_history').add({
        equipmentId,
        userId,
        action: 'return',
        timestamp: firebase.firestore.FieldValue.serverTimestamp()
    });
    return { success: true };
}

// Get categories
async function getCategories() {
    const snapshot = await db.collection('categories').orderBy('name').get();
    return snapshot.docs.map(doc => ({ id: doc.id, ...doc.data() }));
}

// Add category
async function addCategory(name) {
    const docRef = await db.collection('categories').add({
        name,
        createdAt: firebase.firestore.FieldValue.serverTimestamp()
    });
    return { success: true, id: docRef.id };
}

// Get borrow history
async function getBorrowHistory() {
    const snapshot = await db.collection('borrow_history').orderBy('timestamp', 'desc').limit(100).get();
    return snapshot.docs.map(doc => ({ id: doc.id, ...doc.data() }));
}

// Sell equipment
async function sellEquipment(id, equipmentData, price) {
    const batch = db.batch();
    batch.set(db.collection('sales_history').doc(), {
        equipmentId: id,
        equipmentName: equipmentData.name,
        equipmentCategory: equipmentData.category,
        price: price,
        soldAt: firebase.firestore.FieldValue.serverTimestamp(),
        soldBy: auth.currentUser?.uid || 'unknown'
    });
    batch.delete(db.collection('equipment').doc(id));
    await batch.commit();
    return { success: true };
}

// Get sales history
async function getSalesHistory() {
    const snapshot = await db.collection('sales_history').orderBy('soldAt', 'desc').limit(100).get();
    return snapshot.docs.map(doc => ({ id: doc.id, ...doc.data() }));
}
