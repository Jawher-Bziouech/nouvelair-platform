export interface Role {
  id: number;
  nom: string;
}

export interface User {
  id: number;
  nom: string;
  prenom: string;
  email: string;
  role_id: number;
  date_creation?: string | null;
  role?: Role | null;
}

export interface Categorie {
  id: number;
  nom: string;
  description?: string | null;
}

export interface Ressource {
  id: number;
  titre: string;
  type: string;
  contenu?: string | null;
  type_fichier?: string | null;
  chemin_fichier?: string | null;
  categorie_id: number;
  auteur_id: number;
  date_ajout?: string | null;
  est_indexe: boolean;
  categorie?: Categorie | null;
  auteur?: User | null;
}

export interface DashboardStats {
  users: number;
  roles: number;
  categories: number;
  ressources: number;
  ressources_indexees: number;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

export interface Citation {
  id: number;
  ressource_id: number;
  extrait: string;
  score_pertinence?: number | null;
  titre_ressource?: string | null;
}

export interface AssistantMessage {
  id: number;
  session_id: number;
  texte: string;
  role: 'user' | 'assistant' | string;
  date_envoi?: string | null;
  citations: Citation[];
}

export interface AssistantSession {
  id: number;
  utilisateur_id: number;
  date_debut?: string | null;
  date_derniere_activite?: string | null;
}

export interface QuestionResponse {
  session_id: number;
  question: AssistantMessage;
  answer: AssistantMessage;
  mode: 'openai' | 'local' | string;
}
