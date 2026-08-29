const API_BASE_URL =
  "http://127.0.0.1:8000";


async function handleResponse(response) {
  const data = await response.json();

  if (!response.ok) {
    throw new Error(
      data.detail ||
      data.message ||
      "Something went wrong while contacting the server."
    );
  }

  return data;
}


// --------------------------------
// Upload document
// --------------------------------

export async function uploadDocument(file) {
  const formData = new FormData();

  formData.append(
    "file",
    file
  );

  try {
    const response = await fetch(
      `${API_BASE_URL}/upload`,
      {
        method: "POST",
        body: formData,
      }
    );

    return await handleResponse(response);

  } catch (error) {
    if (error.message) {
      throw error;
    }

    throw new Error(
      "Could not connect to the ResearchPilot server."
    );
  }
}


// --------------------------------
// Ask question
// --------------------------------

export async function askQuestion(
  question,
  documentId,
  conversationId = null
) {
  try {
    const requestBody = {
      question,
      document_id: documentId,
    };

    if (conversationId !== null) {
      requestBody.conversation_id =
        conversationId;
    }

    const response = await fetch(
      `${API_BASE_URL}/ask`,
      {
        method: "POST",

        headers: {
          "Content-Type":
            "application/json",
        },

        body: JSON.stringify(
          requestBody
        ),
      }
    );

    return await handleResponse(response);

  } catch (error) {
    if (error.message) {
      throw error;
    }

    throw new Error(
      "Could not connect to the ResearchPilot server."
    );
  }
}


// --------------------------------
// Get conversations for one document
// --------------------------------

export async function getConversations(
  documentId
) {
  try {
    const response = await fetch(
      `${API_BASE_URL}/documents/${encodeURIComponent(
        documentId
      )}/conversations`
    );

    return await handleResponse(response);

  } catch (error) {
    if (error.message) {
      throw error;
    }

    throw new Error(
      "Could not load conversations."
    );
  }
}


// --------------------------------
// Get one conversation
// --------------------------------

export async function getConversation(
  conversationId
) {
  try {
    const response = await fetch(
      `${API_BASE_URL}/conversations/${conversationId}`
    );

    return await handleResponse(response);

  } catch (error) {
    if (error.message) {
      throw error;
    }

    throw new Error(
      "Could not load the conversation."
    );
  }
}


// --------------------------------
// Start a new conversation
// --------------------------------

export async function createConversation(
  documentId
) {
  try {
    const response = await fetch(
      `${API_BASE_URL}/documents/${encodeURIComponent(
        documentId
      )}/conversations`,
      {
        method: "POST",
      }
    );

    return await handleResponse(response);

  } catch (error) {
    if (error.message) {
      throw error;
    }

    throw new Error(
      "Could not create a new conversation."
    );
  }
}


// --------------------------------
// Delete a conversation
// --------------------------------

export async function deleteConversation(
  conversationId
) {
  try {
    const response = await fetch(
      `${API_BASE_URL}/conversations/${conversationId}`,
      {
        method: "DELETE",
      }
    );

    return await handleResponse(response);

  } catch (error) {
    if (error.message) {
      throw error;
    }

    throw new Error(
      "Could not delete the conversation."
    );
  }
}